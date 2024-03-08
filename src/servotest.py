import pyb
import utime

pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)

tim8 = pyb.Timer(8, freq=50)
ch2 = tim8.channel(2, pyb.Timer.PWM, pin=pinC7)

while True:
    
    ch2.pulse_width_percent(7.5)

    utime.sleep(1)

    ch2.pulse_width_percent(2.5)

    utime.sleep(1)
