"""! 
@file bno_test.py
This file reads the euler angles of roll, pitch, and yaw from a BNO055 sensor through the I2C interface. 
"""

from pyb import I2C, Pin
import time
import struct

OPR_MODE_REG = 0x3D # OPR_MODE register addr 
BNO055_I2C_ADDR = 0x28 # BNO055 I2C addr

EULER_REG_START = 0x1A # Euler angle start reg 

i2c = I2C(1, I2C.CONTROLLER, baudrate = 100000)

devices = i2c.scan()

if BNO055_I2C_ADDR in devices:
    
    i2c.mem_write(0x0C, BNO055_I2C_ADDR, OPR_MODE_REG)
    
    time.sleep(1)
    
else:
    raise Exception()

while True:
    
    (yaw, roll, pitch) = struct.unpack('<hhh', i2c.mem_read(6,BNO055_I2C_ADDR,EULER_REG_START))
    
    print("Roll: {:.2f} degrees, Pitch: {:.2f} degrees, Yaw: {:.2f} degrees".format(roll/16.0, pitch/16.0, yaw/16.0))
    
    time.sleep(1)
    

