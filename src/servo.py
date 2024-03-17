"""!
@file servo.py
Implements a Positional Servo wrapper class
"""

import pyb

class Servo:
    def __init__(self, timerChannel, minAngle=0, maxAngle=90, angle=0):
        """!
        Creates a Servo wrapper class
        @param timerChannel The pyb.Timer object corresponding to the signal wire output pin
        @param minAngle The minimum allowable angle the servo can be set to
        @param maxAngle The maximum allowable angle the servo can be set to
        @param angle The angle the servo should be initialized to
        """
        self.channel = timerChannel
        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.write(angle)

    def write(self, angle):
        """!
        This method sets the servo to a specified angle
        @param angle The desired angle
        @returns None
        """
        self.angle = angle
        self.channel.pulse_width_percent(2.5 + 5*max(self.minAngle, min(angle, self.maxAngle))/90)

    def read(self):
        """!
        This method returns the angle that the servo is set to
        @returns int
        """
        return self.angle