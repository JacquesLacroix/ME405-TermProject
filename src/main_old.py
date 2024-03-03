"""!
@file main.py
    This file demonstrates cooperative multitasking and use of cotask and share in checking the inputs and outputs
    of the Nucleo board with a DC motor response.
"""

import gc
import pyb
import cotask
import task_share
import motor_driver
import encoder_reader
import controller
import utime


def task1(shares):
    """!
    This task sets up the pins for motor 1 and calls run() in our controller file- This task then starts the
    step response and prints the values once it's done.
    @returns None
    """
    (kp_share) = shares
    pinC1 = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
    pinA0 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP) 
    pinA1 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    
    pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_PP) 
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)
    
    tim5 = pyb.Timer(5, freq=20000)   #Motor Controller Timer 
    tim8 = pyb.Timer(8, prescaler=1, period=65535)
    
    motor = motor_driver.MotorDriver(pinC1, pinA0, pinA1, tim5)
    encoder = encoder_reader.Encoder(pinC6, pinC7, tim8)

    ctrl = controller.Controller(encoder, motor, 8000, 1/16)
    
    ser = pyb.USB_VCP()
    while True:
        line = ser.readline()
        if line == None:
            yield 0
            continue
        elif line.decode() == "Begin\n":
            while True:
                line = ser.readline()
                if line == None:
                    yield 0
                    continue
                else:
                    kp = line.decode().split("\n")[0]
                    try:
                        kp = float(kp)
                    except:
                        print("End 1")
                        yield 0
                        break
                    kp_share.put(kp)
                    ctrl.set_kp(kp)
                    encoder.zero()
                        
                    startticks = utime.ticks_ms()
                    
                    last = 0
                    
                    while True:
                        current = ctrl.run()
                        if abs(current) < 15 and last - current < .5:
                            for i in range(10):
                                ctrl.run()
                                yield 0
                            break
                        last = current
                        yield 0
                        
                    for i in ctrl.print_list(1, startticks):
                        yield
                    print("End 1")
                    yield 0
                    break
                yield 0
            continue
        else:
            yield 0

def task2(shares):
    """!
    This task performs the same function as task1 but for motor 2.
    @returns None
    """
    (kp_share) = shares
    pinA10 = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
    pinB4 = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP) 
    pinB5 = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
    
    pinB6 = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.OUT_PP) 
    pinB7 = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.OUT_PP)
    
    tim3 = pyb.Timer(3, freq=20000)   #Motor Controller Timer 
    tim4 = pyb.Timer(4, prescaler=1, period=65535)
    
    motor = motor_driver.MotorDriver(pinA10, pinB4, pinB5, tim3)
    encoder = encoder_reader.Encoder(pinB6, pinB7, tim4)

    ctrl = controller.Controller(encoder, motor, 16000, 1/16)

    while True:
        if kp_share.get():
            ctrl.set_kp(kp_share.get())
            
            kp_share.put(0)
            encoder.zero()
                
            startticks = utime.ticks_ms()
            
            last = 0
            
            while True:
                current = ctrl.run()
                if abs(current) < 15 and last - current < .5:
                    for i in range(10):
                        ctrl.run()
                        yield 0
                    break
                last = current
                yield 0
                
            for i in ctrl.print_list(2, startticks):
                pass
            print("End 2")
            yield 0
            continue
        else:
            yield 0
        
            
if __name__ == "__main__":
#     print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
#           "Press Ctrl-C to stop and show diagnostics.")

    # Create a share and a queue to test function and diagnostic printouts
    share0 = task_share.Share('f', thread_protect=False,
                          name="Share 0")
    share0.put(0)

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(task1, name="Task_1", priority=1, period=10,
                        profile=True, trace=False, shares=(share0))
    task2 = cotask.Task(task2, name="Task_2", priority=2, period=10,
                        profile=True, trace=False, shares=(share0))
    
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    
    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # Print a table of task data and a table of shared information data
#     print('\n' + str (cotask.task_list))
#     print(task_share.show_all())
#     print(task1.get_trace())
#     print('')
