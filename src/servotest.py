import pyb
import utime


pinA5 = pyb.Pin(pyb.Pin.board.PA5, pyb.Pin.OUT_PP)
timer2 = pyb.Timer(2, freq=50)
t2ch1 = timer2.channel(1, pyb.Timer.PWM, pin=pinA5)

pinA9 = pyb.Pin(pyb.Pin.board.PA9, pyb.Pin.OUT_PP)
tim1 = pyb.Timer(1, freq=50)
ch2 = tim1.channel(2, pyb.Timer.PWM, pin=pinA9)

while True:
    
    t2ch1.pulse_width_percent(5.8)

    utime.sleep(1)

    t2ch1.pulse_width_percent(5)

    utime.sleep(1)

    ch2.pulse_width_percent(7.5)
    
    utime.sleep(1)
    
    ch2.pulse_width_percent(4)
    
    utime.sleep(1)
    

