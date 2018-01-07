import binascii
import time
import struct
import threading
from bluepy import btle

mac1 = "CC:2F:DE:C6:61:D2"
mac2 = "c5:2c:8a:46:c7:74"
functionID = "713d0002-503e-4c75-ba94-3148f18d941e"
functionIDW = "713d0003-503e-4c75-ba94-3148f18d941e"
time = 100
cont = 0

class MyDelegate(btle.DefaultDelegate):
    cont = 0
    totalBytes = 0
    archivo = None
    device = None
    
    def _init_(self):
        btle.DefaultDelegate(self)
        
    def setUp(self, dev, channel, duration):
        global archivo
        global totalBytes
        global device
        device = dev
        archivo = open(channel,"wb")
        totalBytes = duration * 512
    
    def handleNotification(self, cHandle, data):
        global cont
        global archivo
        global device
        if(cont<totalBytes):
            print(cont)
            print(binascii.b2a_hex(data[0:17]))
            archivo.write(data[0:16])
            cont=cont+16
        elif(cont == totalBytes):
            print("cierra archivo: ",cont, "  total: ",totalBytes)
            archivo.close()
            cont=cont+16
            device.writeCharacteristic(17,"\x00\x00")
            

def readBLE(MacAddress, channel):
    print("Conectando...")
    dev = btle.Peripheral(MacAddress,"random")
    mDelegate = MyDelegate()
    mDelegate.setUp(dev, channel, 5)
    dev.setDelegate(mDelegate)
    print("Conectado!!")
    uuidR = btle.UUID(functionID)
    uuidW = btle.UUID(functionIDW)
    
    try:
        chR1 = dev.getCharacteristics(uuid = uuidR)[0]
        chW1 = dev.getCharacteristics(uuid = uuidW)[0]
        
        print(chR1.valHandle)
        
        i = 0
        dev.writeCharacteristic(chR1.valHandle+1,"\x01\x00")
        chW1.write("1")
        
        while i<=3:
            if dev.waitForNotifications(0.1):
                continue
            print("waiting")
##            valble1 = chR1.read()
##            print(valble1[249]) 
##            valble2= binascii.b2a_hex(valble1[0])
##            print(channel,int(valble2,16)) 
            #archivo.write(valble1)
            i=i+1
            
        
    finally:
        print("Desconectado")
        dev.disconnect()


threads = list()
t1 = threading.Thread(target = readBLE, args = (mac1,"F1.bin"))
threads.append(t1)
t1.start()

##t2 = threading.Thread(target = readBLE, args = (mac2,"F8.bin"))
##threads.append(t2)
##t2.start()
   
