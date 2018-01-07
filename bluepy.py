import binascii
import time
import struct
from bluepy import btle

print("Conectado...")
dev1 = btle.Peripheral("CC:2F:DE:C6:61:D2","random")
dev2 = btle.Peripheral("c5:2c:8a:46:c7:74","random")

"""
childList = dev.getCharacteristics()
print("Handle UUID  Properties")
for ch in childList:
    print("   0x"+format(ch.getHandle(),'02x') + " " + str(ch.uuid) +" " + ch.propertiesToString())
"""
uuidR = btle.UUID("713d0002-503e-4c75-ba94-3148f18d941e")
#uuidR = btle.UUID("0ada1533-98ed-90a2-464a-cec1b735b689")
#uuidW = btle.UUID("713d0003-503e-4c75-ba94-3148f18d941e")
try:
    chR1 = dev1.getCharacteristics(uuid = uuidR)[0]
    chR2 = dev2.getCharacteristics(uuid = uuidR)[0]
  #  chW = dev.getCharacteristics(uuid = uuidW)[0]
    archivo1 = open("CH1.bin","wb")
    archivo2 = open("CH2.bin","wb")
    i = 0
    while 1:
        valble1 = chR1.read()
        valble2 = chR2.read()
        archivo1.write(valble1)
        archivo2.write(valble2)
        valble1= binascii.b2a_hex(valble1[0])
        valble2= binascii.b2a_hex(valble2[0])
        #chW.write(struct.pack('<B',0x02))
        #val11 = binascii.hexlify(val1)
        print("BLE1: ",int(valble1,16),"BLE2: ",int(valble2,16))
        
        i=i+1
        if i==100:
            archivo1.close()
            
            
finally:
    print("Desconectado")
    dev1.disconnect()
