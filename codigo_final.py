# -*- coding: utf-8 -*-

# [START] Imports
import sys
import os
import time
import signal
import threading
import socket
import codecs
import serial
import socket
from os import system
# [END] Imports


mean_tablet = 0.0
d = 0.0

# [START] Connection between tablet and PC via IMU
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('', 13000)
print >> sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
sens = {"3":"Accel m/s^2", "4": "Gyro rad/s", "5": "Mag uT"}

# [END] Connection between tablet and PC via IMU



ser = None

def connect_to_serial():
    global ser
    # Connect to serial port
    possible_ports = ['/dev/ttyUSB0','/dev/ttyUSB1']
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.parity   = 'N'
    ser.rtscts   = False
    ser.timeout  = 1 # Required so that the reader thread can exit
    for p in possible_ports:
        ser.port = p
        try:
            ser.open()
            print "Connected on port: " + p
            return ser
        except:
            time.sleep(1)

def read():
    n = ser.inWaiting()
    data = ser.read(n)
    return data



# [START] Main
def main():



    def get_displacement():

        global mean_tablet
        global d
        
        print_interval = 0
        speed = 0
        first_iter = True


        while True:
    
            # print >> sys.stderr, '\nwaiting to receive message'
            data, address = sock.recvfrom(64)

            print_interval += 1

            # Print 'received %s bytes from %s' % (len(data), address)
            # Print data
            # data = data.replace(".", "") # Eliminates the final "." in the list
            p = data.split(",")
            p = [i.strip() for i in p]

            t = 0

            if(first_iter):
                t = float(p[0])
                first_iter = False
            else:
                t = float(p[0]) - t

            acelleration_x = float(p[2]) # cm/s^2
            speed += acelleration_x * t # Interval in seconds
           
            mean_tablet += speed * t

            mean_neato += 10 * 0.001 
            
            # Print displacemenet
            if print_interval % 25 == 0:
                print "Speed: ", speed, " //" " Displacement: ", mean_tablet
            
    ser = connect_to_serial()
    ser.write("TestMode On\n")
    time.sleep(2)
    data = read()
    #print(data)

    ser.write("GetAnalogSensors\n")
    time.sleep(0.1)
    data = read()

    # Initialize IMU integrator

    import threading

    parallel_imu = threading.Thread(target=get_displacement)
    parallel_imu.start()

    # Neato walks 200 mm five times (totalling 1 meter)
    a = 0
    t0 = time.time()
    d = 0
    while a < 5:
        ser.write("SetMotor {0} {1} {2}\n".format(200, 200, 100))
        time.sleep(3) 
        a+=1 
        d += 20
    print("DONE")

    # Measurement uncertainty (tablet): 1cm
    # Measurement uncertainty (Neato): 1cm

    # To calculate the robot's probable position, we use the Kalman Filter: we multiply
    # two normal distributions, being the resulting mean the position with highest probability
    # of being correct; and the standard deviation the measurement uncertainty. 

    std_neato = 1
    std_tablet = 1

    global mean_tablet
    global mean_neato

    new_mean = (mean_tablet * (std_neato**2) + mean_neato * (std_tablet**2)) / ((std_neato**2) + (std_tablet**2))
    uncertainty = ( float(((std_neato**2) * (std_tablet**2))) / ((std_neato**2) + (std_tablet**2)) ) ** 0.5
    print(str(new_mean))
    print(str(uncertainty))
# [END] Main

main()