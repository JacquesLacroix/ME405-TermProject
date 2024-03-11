"""! 
@file controller.py
Implements a porportional gain controller for a DC motor with a quadrature encoder
"""
import encoder_reader
import motor_driver
import utime

class Controller:
    """!
    This class implements a proportional gain controller for a DC motor with quadrature encoder
    """
    def __init__(self, encoder, motor, setpoint, kp, ticks=8000, gearRatio=1):
        """!
        Create a DC motor controller object with proportional gain from quadrature encoder feedback
        @param encoder The encoder object used to measure position
        @param motor The motor driver used to send signals to the motor
        @param setpoint The target position for the motor to turn to
        @param kp The proportional gain coefficient for the controller to use
        @param ticks The number of encoder ticks corresponding to 1 full rotation
        @param gearRatio The gear speed reduction ratio, allowing for angles to be set on the output shaft (Output Gear Teeth/Motor Pinion Teeth).
        A positive ratio should be used for odd numbers of gears, and a negative ratio should be used for even numbers of gears to ensure the output
        shaft rotates in the desired direction. The ratio should be negated if the motor is mounted upside-down relative to the output shaft.
        @returns Controller
        """
        self.encoder = encoder
        self.motor = motor
        self.set_setpoint(setpoint)
        self.set_kp(kp)
        self.times = []
        self.positions = []
        self.ticks = ticks
        self.gearRatio = gearRatio
        
    def run(self):
        """!
        Runs one step of the control loop. Changes motor's pulse width and logs the current time and encoder position
        @returns None
        """
        position = self.encoder.read()
        PWM = self.kp*(self.setpoint - position)
        self.motor.set_duty_cycle(PWM)
        self.positions.append(position) 
        self.times.append(utime.ticks_ms())
        return PWM
    
    def set_setpoint(self, setpoint):
        """!
        Allows the user to change the motor's target position
        @param setpoint The position for the motor to turn to
        @returns None
        """
        self.setpoint = setpoint

    def setAngle(self, angle):
        """!
        Allows the user to input a desired angle on the output shaft
        @param angle The desired output shaft angle
        @returns None
        """
        self.setpoint = self.angleToTicks(angle)

    def readAngle(self):
        """!
        Allows the user to read the current angle of the output shaft
        @returns int
        """
        return self.ticksToAngle(self.encoder.read())
        
    def set_kp(self, kp):
        """!
        Allows the user to change the controller's porportional gain coefficent
        @param kp The Kp value to set the controller's proportional gain to
        @returns None
        """
        self.kp = kp
        
    def print_list(self, task, start):
        """!
        Prints and clears all time and position pairs logged
        @param start Time in milliseconds at which the response test began
        @returns None
        """
        for i in range(len(self.times)):
            print(f"{task}, {(self.times[i] - start):d}, {self.positions[i]:d}")
            yield
        self.times = []
        self.positions = []

    def angleToTicks(self, angle):
        """!
        Converts a specified angle into a encoder ticks
        @param angle The angle to be converted
        @returns int
        """
        return angle * self.ticks * self.gearRatio / 360

    def ticksToAngle(self, ticks):
        """!
        Converts a specified number of encoder ticks into an angle
        @param ticks The number of ticks to be converted
        @returns int
        """
        return ticks * 360 // (self.ticks * self.gearRatio)
    
if __name__ == "__main__":
    
    pinC1 = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
    pinA0 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP) 
    pinA1 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    
    pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_PP) 
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)
    
    tim5 = pyb.Timer(5, freq=20000)   #Motor Controller Timer 
    tim8 = pyb.Timer(8, prescaler=1, period=65535)
    
    motor = motor_driver.MotorDriver(pinC1, pinA0, pinA1, tim5)
    encoder = encoder_reader.Encoder(pinC6, pinC7, tim8)
    
    setpoint = 1600
    
    controller = Controller(encoder, motor, setpoint, 1/16)
    
    while True:
        
        kp = input("ENTER KP VALUE: ")
        try:
            kp = float(kp)
        except:
            print("KP MUST BE NUMBER, DUMB DUMB")
            continue
        
        controller.set_kp(kp)
        encoder.zero()
        
        startticks = utime.ticks_ms()
        
        while not abs(controller.run()) < 10:        
            utime.sleep_ms(10)
        
        controller.print_list(startticks)