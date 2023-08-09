import machine
from machine import I2C, Pin, ADC
from modules.dht_module import device
import time
import pycom
import _thread
from modules.lora_module import join_lora, send_lora
#from modules.bme280 import BME280, BME280_OSAMPLE_16
import ustruct
from modules.deepsleep import DeepSleep, PIN_WAKE, TIMER_WAKE, POWER_ON_WAKE


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
    
pycom.heartbeat(False)

def measure_sensor():
    global payload
    dht = device(machine.Pin.exp_board.G22)
    
    if dht.trigger() == True:
        temp = dht.temperature
        hum = dht.humidity
    else:
        print("sensor values could not be read dht trigger is false")
    
    print(" [+] Temp: " + str(temp) + ", Humidity: " + str(hum))

    hum = int(float(hum) * 10)                 # 2 Bytes
    temp = int(float(temp)*10) + 400           # max -40°, use it as offset

    print("humidity" , hum)
    print("temparature", temp)
    
    #No sensors attached:
    light = 0
    windspeed = 0
    winddirection = 0
    press = 0

    print(" [***] temp: ", temp, "hum: ", hum, "press: ", press, "light:", light, "windspeed:", windspeed, "winddirection: ", winddirection)

    ht_bytes = ustruct.pack('HHHHHH', hum, temp, press, light, windspeed, winddirection)
    print("ht_bytes:", ht_bytes)
    for i in range(len(ht_bytes)):
        payload.append(ht_bytes[i])


if __name__ == "__main__":
    print("starting main yellow nr3")
    time.sleep(1)

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
    #i2c.deinit()
    
    time.sleep(1)
    ds.go_to_sleep(10)


  