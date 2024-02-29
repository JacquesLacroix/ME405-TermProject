"""! 
@file motor_driver.py
Runs motor in desired direction at provided speed level.
"""

import pyb
import time

class MotorDriver:
    """! 
    This class implements a motor driver for an ME405 kit. 
    """

    def __init__ (self, en_pin, in1pin, in2pin, timer):
        """! 
        Creates a motor driver by initializing GPIO
        pins and turning off the motor for safety. 
        @param en_pin motor enable pin
        @param in1pin pin corresponding to timer channel 1 pin
        @param in2pin pin corresponding to timer channel 2 pin
        @param timer timer used for PWM
        @returns MotorDriver
        """
#       print ("Creating a motor driver")
        
        self.ENA = en_pin
        self.ch1 = timer.channel(1, pyb.Timer.PWM, pin=in1pin)
        self.ch2 = timer.channel(2, pyb.Timer.PWM, pin=in2pin)

    def set_duty_cycle (self, level):
        """!
        This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
               cycle of the voltage sent to the motor
        @returns None
        """
#       print (f"Setting duty cycle to {level}")
        if level == 0:
            self.ENA.low()
            return
        self.ENA.high()
        if level > 0:
            self.ch1.pulse_width_percent(level if level <= 100 else 100)
            self.ch2.pulse_width_percent(0)
        else:
            self.ch1.pulse_width_percent(0)
            self.ch2.pulse_width_percent(-1*level if level >= -100 else 100)
            
if __name__ == '__main__':
    pinA10 = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
    pinB4 = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP) 
    pinB5 = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
    
    tim3 = pyb.Timer(3, freq=20000)

    motor = MotorDriver(pinA10, pinB4, pinB5, tim3)
    
    motor.set_duty_cycle(150)

    time.sleep(1)
    
    motor.set_duty_cycle(-150)

    time.sleep(1)

    motor.set_duty_cycle(50)
    
    time.sleep(1)
    
    motor.set_duty_cycle(0)