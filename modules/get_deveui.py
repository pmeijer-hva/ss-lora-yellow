from network import LoRa
import binascii
#print(LoRa.mac())
print(binascii.hexlify(LoRa().mac()).upper())