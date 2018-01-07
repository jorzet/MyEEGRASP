import binascii
import time
import struct
import threading
import json
import os
import subprocess
from bluepy import btle
from bluetooth import *

##################################################################
## Created 03/12/17
## Authors :
##          Fernando Hernandez Molina
##          Jorge Zepeda Tinoco
##
## This program creates a rfcomm between smartphone and raspberry
## and creates a BLE notification services to get EEG signals
## between each node and raspberry
##
##################################################################


## macros to set up BluetoothSocket with Android
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
jsonUser = ""

## macros to set up BLE
functionIDR = "713d0002-503e-4c75-ba94-3148f18d941e"
functionIDW = "713d0003-503e-4c75-ba94-3148f18d941e"
isRunning=[True]*3
cont =[0]*3
channels=[""]*3
devices=[0]*3
files=[0]*3

## macro to restart program when finish
runningProgram = True

##  this class listen the BLE status and write incoming data into bin file
class MyDelegate(btle.DefaultDelegate):
    idThread = 0
    totalBytes = 0
    archivo = None
    device = None
    
    
    def _init_(self):
        btle.DefaultDelegate(self)
        
    def setUp(self,idThread, channel, duration):
        global totalBytes
        files[idThread] = open(("/home/pi/Documents/RaspberryRecordings/REC/"+channel),"wb")
        totalBytes = duration * 512
        print(totalBytes)
    
    def handleNotification(self, cHandle, data):
        
        print(binascii.b2a_hex(data[0:18]))
        idDevice = int(data[17].encode('hex'),16)
        print("idDevice: ",idDevice, "poorQuality: ",binascii.b2a_hex(data[16]))

        if(cont[idDevice]<totalBytes):
            print(cont)
            files[idDevice].write(data[0:16])
            cont[idDevice]=cont[idDevice]+16
            
        elif(cont[idDevice] == totalBytes):
            print("cierra archivo: ",cont, "  total: ",totalBytes)
            files[idDevice].close()
            cont[idDevice]=cont[idDevice]+16
            devices[idDevice].writeCharacteristic(17,"\x00\x00")
            isRunning[idDevice] = False

## this thread creates a BLE notification service
def readBLE(MacAddress, channel, duration, idThread):
    print("Conectando...")

    
    
    dev = btle.Peripheral(MacAddress,"random")
    devices[idThread] = dev
    channels[idThread] = channel
    
    mDelegate = MyDelegate()
    mDelegate.setUp(idThread, channel, duration)
    dev.setDelegate(mDelegate)
    print("Conectado!!")
    uuidR = btle.UUID(functionIDR)
    uuidW = btle.UUID(functionIDW)
    try:
        chR = dev.getCharacteristics(uuid = uuidR)[0]
        chW = dev.getCharacteristics(uuid = uuidW)[0]
        
        start_time = time.time()
        valble1 = []
        i = 0
        dev.writeCharacteristic(chR.valHandle+1,"\x01\x00")
        chW.write("1")
        
        while isRunning[idThread] is True:
            if dev.waitForNotifications(0.1):
                continue
            print("waiting")
            i=i+1
        
        
    except KeyboardInterrupt:
        dev.disconnect()
        isRunning[idThread] = False
    finally:
        print("Desconectado")
        dev.disconnect()
        isRunning[idThread] = False

## this thread check the thread status
## if all the threads status is finished it calls the RaspberryClientWS
## to send the recording to server
def checkThreads():
    isFinished = False
    while not isFinished:
        isFinished = not any(isRunning)
    print("isFinished: True")
    statusFile = open("/home/pi/Documents/RaspberryRecordings/statusFile.txt", 'wr+')
    currentStatus = statusFile.write('1')
    statusFile.close()

    print(not isFinished)  
    try:
        salida = subprocess.check_output("java RaspberryClientWS",stderr= subprocess.STDOUT,shell=True)
            
        print(salida)
        runningProgram = True
    except subprocess.CalledProcessError, ex:
        print(ex.cmd)
        print(ex.message)
        print(ex.returncode)
        print(ex.output)
            


########################################################################
############################## main exceution  #########################
########################################################################
## check raspberry current status
## if is sending to server not request data user
## if is to recording send a request data user    

while True:
    
    if(os.path.exists("/home/pi/Documents/RaspberryRecordings/statusFile.txt")):

        statusFile = open("/home/pi/Documents/RaspberryRecordings/statusFile.txt", 'r')
        currentStatus = statusFile.read(1)
        print('currentStatus: ',currentStatus)
        statusFile.close()
    else:
        statusFile = open("/home/pi/Documents/RaspberryRecordings/statusFile.txt", 'wr+')
        statusFile.write("0")
        currentStatus = statusFile.read(1)
        print('currentStatus: ',currentStatus)
        statusFile.close()


    if(currentStatus == '0' or currentStatus == ''):
        isRunning=[True]*3
        cont =[0]*3
        channels=[""]*3
        devices=[0]*3
        files=[0]*3
        
        print("espera conexion")
        ## creates a RFMCOMM socket to get data from smartphone        
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
            ## waits a bluetooth connection    
            clientSocket, clientInfo = serverSocket.accept()
            print("conexion aceptada a: ", clientInfo)
                        
            clientSocket.send('connection_successfully')

            ## recives data user    
            data = clientSocket.recv(1024)
            print(data)
            mJson = json.loads(data)
            print(mJson['id_patient'])

            ## save data user into json file    
            with open('/home/pi/Documents/RaspberryRecordings/infoSchedule.txt','wr') as infoSchedule:
                json.dump(data, infoSchedule)

            ## gets data recived from json
            channels = mJson['channels']
            mac_address = mJson['mac_address']
            duration = mJson['duration']
            print(duration)

            ## close socket to start recording
            print("closing socket")
            clientSocket.close()

            ## wait bluetooth connection to satrt recording    
            clientSocket, clientInfo = serverSocket.accept()
            print("conexion aceptada a: ", clientInfo)

            ## recives recording status
            start = clientSocket.recv(1024)
            print(start)

            ## close socket to start recording
            print("closing socket")
            clientSocket.close()

            ## if recives 1 starts recording
            ## if receives 0 do nothing and close socket
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
                isRunning = [True]*len(channels)

                ## creates all threads according to channels        
                for i in range(len(channels)):
                    jsonChannels = channels[i]
                    jsonMacs = mac_address[i]
                    print('channel: ',str(jsonChannels['channel'])," mac: ",str(jsonMacs['mac']))
                    t1 = threading.Thread(target = readBLE, args = (jsonMacs['mac'],(jsonChannels['channel']+".bin"),total_seconds, i))
                    threads.append(t1)
                    t1.start()

                ## creates thread to check channels threads status            
                t = threading.Thread(target = checkThreads)
                t.start()

                statusFile = open("/home/pi/Documents/RaspberryRecordings/statusFile.txt", 'wr+')
                statusFile.write("2")
                currentStatus = statusFile.read(1)
                statusFile.close()
                print('currentStatus: ',currentStatus)
                        
                        
        except:
            e = sys.exc_info()[0]
            print(e)
            print("closing socket")
            clientSocket.close()
            serverSocket.close()

                    ## flag to not run again threads
        ##            runningProgram = False
                        

    else:
        try:
            salida = subprocess.check_output("java RaspberryClientWS",stderr= subprocess.STDOUT,shell=True)
                                
            print(salida)
        except subprocess.CalledProcessError, ex:
            print(ex.cmd)
            print(ex.message)
            print(ex.returncode)
            print(ex.output)

