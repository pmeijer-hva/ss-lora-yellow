from network import LoRa
import socket
import time
import ubinascii

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an OTAA authentication parameters, change them to the provided credentials
app_eui = ubinascii.unhexlify('0000000000000000')
app_key = ubinascii.unhexlify('094ED5FC2F84368DD8CB349CB75BAE03')
#uncomment to use LoRaWAN application provided dev_eui
dev_eui = ubinascii.unhexlify('70B3D5499DDE0C64')

# Uncomment for US915 / AU915 & Pygate
# for i in range(0,8):
#     lora.remove_channel(i)
# for i in range(16,65):
#     lora.remove_channel(i)
# for i in range(66,72):
#     lora.remove_channel(i)


# blocking routine if not joined yet
def join_lora():
    # join a network using OTAA (Over the Air Activation)
    #uncomment below to use LoRaWAN application provided dev_eui
    print("try to join...")
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
    #lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        #time.sleep(7)
        print('Not yet joined...')

    # join_wait = 0
    # while lora.has_joined():
    #     print('Not joined yet...')
    #     join_wait += 1
    #     if join_wait == 5:
    #         lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0, dr=0)
    #         join_wait = 0
    #     else:
    #         break
    #     time.sleep(2.5)


    print('Joined')
    
    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    # set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    return(s)


def send_lora(s, data):
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)

    # send some data
    s.send(bytes(data))

    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    s.setblocking(False)

    # get any data received (if any...)
    data = s.recv(64)
    print(data)
    return(data)



if __name__ == "__main__":

    print("starting main")
    period = 3

    print("start lora")
    sckt = join_lora()
    time.sleep(2)

    payload = []

    while True:
        #print("On")
        #p_out.value(1)

        #print(" [+] Temp: " + bme.temperature + ", Pressure: " + bme.pressure + ", Humidity: " + bme.humidity)

        #time.sleep(0.2)
        #p_out.value(0)
        #print("Off")
        #measure_sensor()
        time.sleep(3)
        payload = [0xF1, 0xE2, 0xD3]

        print("LORA:", payload)
        if len(payload) != 0:
            send_lora(sckt, payload)
            payload = []
            #confirm with LED
            #pycom.rgbled(0x0000FF)  # Blue
            #time.sleep(0.1)
            #pycom.rgbled(0x000000)  # Off
            #time.sleep(1.9)
        time.sleep(period)