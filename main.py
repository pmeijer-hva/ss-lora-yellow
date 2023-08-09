import machine
from machine import I2C, Pin, ADC
from modules import dht_module
import time
import pycom
import _thread
from modules.lora_module import join_lora, send_lora
from modules.bme280 import BME280, BME280_OSAMPLE_16
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
    temp = bme.temperature
    hum = bme.humidity
    press = bme.pressure
    print(" [+] Temp: " + temp + ", Pressure: " + press + ", Humidity: " + hum)
    hum = int(float(hum) * 10)                 # 2 Bytes
    temp = int(float(temp)*10) + 400           # max -40°, use it as offset
    press = int(float(press) * 10)            # 300 to 1100 hPa with 2 digits after the point
    
    #No sensors attached:
    light = 0
    windspeed = 0
    winddirection = 0

    print(" [***] temp: ", temp, "hum: ", hum, "press: ", press, "light:", light, "windspeed:", windspeed, "winddirection: ", winddirection)

    ht_bytes = ustruct.pack('HHHHHH', hum, temp, press, light, windspeed, winddirection)
    print("ht_bytes:", ht_bytes)
    for i in range(len(ht_bytes)):
        payload.append(ht_bytes[i])


if __name__ == "__main__":
    print("starting main yellow nr3")
    time.sleep(1)

    # light sensor init
    adc = ADC()             # create an ADC object for the light sensor
    apin_lightsensor = adc.channel(pin='P13', attn = ADC.ATTN_11DB)   # create an analog pin on P13, 3.3V reference, 12bit


    # mind the pinout of the LOPY and MAKR Module 2.0
    i2c = I2C(0, pins=('P10','P9'))     # create and use non-default PIN assignments (P10=SDA, P11=SCL)
    i2c.init(I2C.MASTER, baudrate=20000) # init as a master
    i2c = I2C(0, I2C.MASTER, baudrate=400000)
    print(i2c.scan())
    bme = BME280(i2c=i2c, mode=BME280_OSAMPLE_16)
    
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


  