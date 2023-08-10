import machine
from machine import I2C, Pin, ADC
from modules.dht_module import device
import time
import pycom
import _thread
from modules.lora_module import join_lora, send_lora
import ustruct
from modules.deepsleep import DeepSleep, PIN_WAKE, TIMER_WAKE, POWER_ON_WAKE
import modules.soundsensor as soundsensor


# global variables
# update periode in seconds for measuring a sending
period = 3    
ds = DeepSleep()
# get the wake reason and the value of the pins during wake up
wake_s = ds.get_wake_status()
print(wake_s)

if wake_s['wake'] == PIN_WAKE:
    print("Pin wake up")

elif wake_s['wake'] == TIMER_WAKE:
    print("Timer wake up")

else:  # POWER_ON_WAKE:
    print("Power ON reset")
    


def measure_sensor():
    #todo refactor into smaller methods
    global payload

    light = read_lightsensor()  
    time.sleep(1)
    sound = read_soundsensor() 
    time.sleep(1)
    array = read_humtemp_sensor()
    hum = array[0]
    temp = array[1]
       
    print(" [***] temp: {} hum: {} sound: {} light: {}".format(temp,hum, sound,light))
    
    append_payload(temp,hum,light,sound)
    



def read_lightsensor():
    try:
        return apin_lightsensor() 
    except:
        return 0

def read_soundsensor():      
    try:
        return soundsensor.running_average(apin_soundsensor) 
    except:
        return 0
    
def read_humtemp_sensor():
    try:
        for _ in range(10):
            if dht.trigger() == True:
                hum = int(dht.humidity * 10)                 # 2 Bytes
                temp = int(dht.temperature*10) + 400         # max -40°, use it as offset
                return [hum,temp]
            else:
                print(dht.status + "sensor values could not be read, dht trigger is false") 
                time.sleep(1) 
    except:
        return [0,0]
    
    
def append_payload(temp,hum,light,sound):
    ht_bytes = ustruct.pack('HHHHHH', temp, hum, light, sound)
    print("ht_bytes:", ht_bytes)
    for i in range(len(ht_bytes)):
        payload.append(ht_bytes[i])
     

if __name__ == "__main__":
    pycom.heartbeat(True)
    print("starting main yellow nr3")
    time.sleep(1)
    
    adc = ADC()             # create an ADC object for the light sensor
    apin_lightsensor = adc.channel(pin='P13', attn = ADC.ATTN_11DB)   # create an analog pin on P13, 3.3V reference, 12bit
    apin_soundsensor = adc.channel(pin='P15', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P13

    dht = device(machine.Pin.exp_board.G22)

    # blocking joining lora
    sckt = join_lora()
    time.sleep(2)
    # global data buffer
    payload = []            # common data buffer to collect and send
    
    # get sensor values in payload
    measure_sensor()
    time.sleep(3)
    
    if len(payload) != 0:
        print("about to send data")
        data = send_lora(sckt, payload)
        
    else:
        data = 0
        print("no lora sent!")

    print("going sleeping")
    
    time.sleep(1)
    ds.go_to_sleep(60)


  