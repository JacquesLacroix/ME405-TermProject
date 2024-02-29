"""! 
@file encoder_reader.py
Reads absolute position of quadrature encoder.
"""
import time
import pyb

class Encoder:
    """! 
    This class implements a quadrature encoder.
    """    
    def __init__ (self, in1pin, in2pin, timer):
        """! 
        Create an encoder driver and initalizes both it and
        a timer used in updating its position.
        @param in1pin pin corresponding to timer channel 1 pin
        @param in2pin pin corresponding to timer channel 2 pin
        @param timer timer used for reading encoder
        @returns Encoder
        """    
        ch1 = timer.channel(1, pyb.Timer.ENC_AB, pin=in1pin)
        ch2 = timer.channel(2, pyb.Timer.ENC_AB, pin=in2pin)
        
        self.timer = timer
        
        self.zero()
        
    def read(self):
        """!
        This method updates the position of the encoder, accounting for any overflows, and returns the current absolute position of the encoder.
        @returns position
        """
        new = self.timer.counter()
        
        delta = new - self.last
        
        self.last = new
        
        if delta > 32768:
            self.value -= 65535 - delta
        elif delta < -32768:
            self.value += 65535 + delta
        else:
            self.value += delta
        return self.value
    
    def zero(self):
        """!
        This method sets current position to zero.
        @returns None
        """
        self.value = 0
        self.last = 0
        self.timer.counter(0)
        
        
if __name__ == '__main__':
    pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_PP) 
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)

    tim8 = pyb.Timer(8, prescaler=1, period=65535)

    encoder = Encoder(pinC6, pinC7, tim8)
    
    count = 0
    
    while True:
        count += 1
        if count == 100:
            encoder.zero()
            count = 0
        print(encoder.read())
        time.sleep(.1)