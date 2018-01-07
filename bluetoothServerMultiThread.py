import binascii
import time
import struct
import threading
import json
import subprocess
from bluepy import btle
from bluetooth import *

# macros to set up BluetoothSocket with Android
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
jsonUser = ""

# macros to set up BLE
mac1 = "CC:2F:DE:C6:61:D2"
mac2 = "c5:2c:8a:46:c7:74"
functionID = "713d0002-503e-4c75-ba94-3148f18d941e"
isRunning=[True]*2


def readBLE(MacAddress, channel, duration, idThread):
    print("Conectando...")
    dev = btle.Peripheral(MacAddress,"random")
    print("Conectado!!")
    uuidR = btle.UUID(functionID)
    try:
        chR1 = dev.getCharacteristics(uuid = uuidR)[0]
        archivo = open(("/home/pi/Documents/RaspberryRecordings/REC/"+channel),"wb")
        start_time = time.time()
        valble1 = []
        while (time.time() - start_time) < duration:
            valble1.append(chR1.read())
            valble2= binascii.b2a_hex(valble1[0])
            print(channel,int(valble2,16)) 
            
        for i in range(len(valble1)):
            archivo.write(valble1[i])
        
        print("cierra archivo")
        archivo.close()
    except KeyboardInterrupt:
        dev.disconnect()
        isRunning[idThread] = False
    finally:
        print("Desconectado")
        dev.disconnect()
        isRunning[idThread] = False

            
def checkThreads():
    isFinished = False
    while not isFinished:
        isFinished = not any(isRunning)
        
    print(not isFinished)  
    try:
        
        salida = subprocess.check_output("java RaspberryClientWS",stderr= subprocess.STDOUT,shell=True)
            
        print(salida)
    except subprocess.CalledProcessError, ex:
        print(ex.cmd)
        print(ex.message)
        print(ex.returncode)
        print(ex.output)
            

serverSocket = BluetoothSocket( RFCOMM )
serverSocket.bind(("", PORT_ANY))
serverSocket.listen(1)

port = serverSocket.getsockname()[1]

advertise_service(serverSocket, "EEGPiServer",
                            service_id = uuid,
                            service_classes = [ uuid, SERIAL_PORT_CLASS ],
                            profiles = [ SERIAL_PORT_PROFILE ]
                            #protocols = [ OBEX_UUID ]
                            )

print("Esperando conexion en el puerto: ", port)
try:
    clientSocket, clientInfo = serverSocket.accept()
    print("conexion aceptada a: ", clientInfo)
    clientSocket.send('connection_successfully')
    data = clientSocket.recv(1024)
    print(data)
    mJson = json.loads(data)
    print(mJson['id_patient'])
    with open('/home/pi/Documents/RaspberryRecordings/infoSchedule.txt','wr') as infoSchedule:
        json.dump(data, infoSchedule)

    channels = mJson['channels']
    mac_address = mJson['mac_address']
    duration = mJson['duration']
    print(duration)
    
    print("closing socket")
    clientSocket.close()

    clientSocket, clientInfo = serverSocket.accept()
    print("conexion aceptada a: ", clientInfo)
    start = clientSocket.recv(1024)
    print(start)
    if(start == '1'):
        print("inicia grabacion")
        split_duration = duration.split(":")
        print(split_duration)
        seconds = int(split_duration[2])
        minutes = int(split_duration[1])
        hours = int(split_duration[0])
        total_seconds = seconds + (minutes*60) + (hours*3600)
        print(total_seconds)
        threads = list()
        isRunning=[True]*len(channels)
        
        for i in range(len(channels)):
            jsonChannels = channels[i]
            jsonMacs = mac_address[i]
            print('channel: ',str(jsonChannels['channel'])," mac: ",str(jsonMacs['mac']))
            t1 = threading.Thread(target = readBLE, args = (jsonMacs['mac'],(jsonChannels['channel']+".bin"),total_seconds, i))
            threads.append(t1)
            t1.start()

        t = threading.Thread(target = checkThreads)
        t.start()
        
    
except:
    e = sys.exc_info()[0]
    print(e)
    print("closing socket")
    clientSocket.close()
    serverSocket.close()

##threads = list()
##t1 = threading.Thread(target = readBLE, args = (mac1,"F1.bin"))
##threads.append(t1)
##t1.start()
##
##t2 = threading.Thread(target = readBLE, args = (mac2,"F8.bin"))
##threads.append(t2)
##t2.start()
##   
