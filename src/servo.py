import pyb

class Servo:
    def __init__(self, timerChannel, minAngle=0, maxAngle=90, angle=0):
        self.channel = timerChannel
        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.write(angle)

    def write(self, angle):
        self.angle = angle
        self.channel.pulse_width_percent(2.5 + 5*max(self.minAngle, min(angle, self.maxAngle)))

    def read(self):
        return self.angle