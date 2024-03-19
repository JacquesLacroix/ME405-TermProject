"""!
@file main.py
This program controls all aspects of the turret and is responsible for software and hardware interaction
"""

import pyb
import cotask
import task_share
import utime
from motor_driver import MotorDriver
from encoder_reader import Encoder
from controller import Controller
from servo import Servo
from mlx_cam import MLX_Cam
from machine import I2C
import gc

def task1(shares):
    """!
    This task handles turning the panning axis of the turret
    @param shares A tuple of shared variables between tasks
    @returns None
    """
    (hAngle, start, readyForImage, vAngle, fire) = shares

    state = 0

    hAngle.put(0)
    readyForImage.put(0)
    
    pinA10 = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
    pinB4 = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP) 
    pinB5 = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
    
    pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_PP) 
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)
    
    tim3 = pyb.Timer(3, freq=20000)
    
    tim8 = pyb.Timer(8, prescaler=1, period=65535)
    
    motor = MotorDriver(pinA10, pinB4, pinB5, tim3)
    
    encoder = Encoder(pinC6, pinC7, tim8)
    
    ctrl = Controller(encoder, motor, 0, kp=0.06, ki=0, kd=0.0002, ticks=8000, gearRatio=float(96)/float(30))
    
    closeEnough = const(3)

    yield

    while True:
        #print(state)
        if state == 0:
            # Waiting for start
            if start.get():
                ctrl.set_kp(0.06)
                ctrl.set_kd(0.0002)
                hAngle.put(-180)
                ctrl.setAngle(hAngle.get())
                state = 2
            yield
        elif state == 1:
            # Idle
            if abs(hAngle.get() - ctrl.readAngle()) > closeEnough:      
                ctrl.setAngle(hAngle.get())
                readyForImage.put(0)
                state = 2
            elif not start.get():
                readyForImage.put(0)
                state = 0
            yield
        elif state == 2:
            # Panning
            ctrl.run()
            if abs(hAngle.get() - ctrl.readAngle()) <= closeEnough: # May need to change this
                for i in range(3):
                    ctrl.run()
                ctrl.motor.set_duty_cycle(0)
                ctrl.set_kp(0.2)
                ctrl.set_kd(0.01)
                if start.get():
                    readyForImage.put(1)
                    state = 1
                else:
                    state = 1
            yield
        else:
            raise ValueError(f"Invalid Task 1 State: {state}")

def task2(shares):

    """!
    This task handles the start button
    @param shares A tuple of shared variables between tasks
    @returns None
    """
    (hAngle, start, readyForImage, vAngle, fire) = shares

    start.put(0)

    state = 0

    pinB10 = pyb.Pin(pyb.Pin.board.PB10, pyb.Pin.IN)
    
    counter = 0

    yield

    while True:
        if state == 0:
            # Waiting
            if not pinB10.value():
                start.put(1)
                fire.put(0) 
                state = 1
                counter = 0
            yield 
        elif state == 1:
            # Start
            if not start.get():
                state = 0
            yield
        else:
            raise ValueError(f"Invalid Task 2 State: {state}")

def task3(shares):
    """!
    This task handles turning the vertical axis of the turret
    @param shares A tuple of shared variables between tasks
    @returns None
    """
    (hAngle, start, readyForImage, vAngle, fire) = shares

    state = 0

    vAngle.put(45)

    pinA5 = pyb.Pin(pyb.Pin.board.PA5, pyb.Pin.OUT_PP)
    timer2 = pyb.Timer(2, freq=50)
    t2ch1 = timer2.channel(1, pyb.Timer.PWM, pin=pinA5)
    vServo = Servo(t2ch1, angle=vAngle.get(), minAngle=45, maxAngle=60)

    yield

    while True:
        if state == 0:
            # Waiting for start
            if start.get():
                state = 1
            yield
        elif state == 1:
            # Normal Operation
            if vAngle.get() != vServo.read():
                vServo.write(vAngle.get())
                yield
            if not start.get():
                state = 0
            yield
        else:
            raise ValueError(f"Invalid Task 3 State: {state}")

def task4(shares):
    """!
    This task handles taking images and setting angles
    @param shares A tuple of shared variables between tasks
    @returns None
    """
    (hAngle, start, readyForImage, vAngle, fire) = shares

    state = 0

    fire.put(0)

    pinB8 = pyb.Pin(pyb.Pin.board.PB8, pyb.Pin.ALT, alt=4)
    pinB9 = pyb.Pin(pyb.Pin.board.PB9, pyb.Pin.ALT, alt=4)
    i2c = I2C(1)
    camera = MLX_Cam(i2c)
    image = None
    arrayImage = []
    vMax = 0
    hMax = 0
    
    hOffset = const(-10)
    vOffset = const(-16)
    hScale = const(0.95)
    vScale = const(1)

    yield

    while True:
        if state == 0:
            # Waiting for start
            if start.get():
                state = 1
            yield
        elif state == 1:
            # Normal Operation
            if readyForImage.get():
                while not image:
                    image = camera.get_image_nonblocking()
                    yield
                for line in camera.get_csv(image):
                    arrayImage.append(line.split(","))
                    yield
                for (hIdx, line) in enumerate(arrayImage):
                    if hIdx < 4:
                        continue
                    for (vIdx, pixel) in enumerate(line):
                        try:
                            if float(pixel) > float(arrayImage[hMax][vMax]):
                                vMax = vIdx
                                hMax = hIdx
                        except:
                            raise ValueError("Camera returned non-number data")
                    yield
                
                hNew = int(hAngle.get() + hScale*(hMax + hOffset))
                vNew = int(vScale*(max(vMax, 16) + vOffset) + 43)
                
                print("-------Next--------")
                print("Maximum Heat Signature:")
                print(hMax)
                print(vMax)
                print("Pointing at:")
                print(hAngle.get())
                print(vAngle.get())
                print("Where to go:")
                print(hNew)
                print(vNew)
                
                if abs(hNew - hAngle.get()) <= 1 and abs(vNew - vAngle.get()) <= 1:
                    fire.put(1)
                    print("Fire!")
                else:
                    hAngle.put(hNew)
                    vAngle.put(vNew)
                image = None
                arrayImage = []
                vMax = 0
                hMax = 0
                state = 0
                
            yield
            
        else:
           raise ValueError(f"Invalid Task 4 State: {state}") 

def task5(shares):
    """!
    This task handles actutating the trigger
    @param shares A tuple of shared variables between tasks
    @returns None
    """
    (hAngle, start, readyForImage, vAngle, fire) = shares

    state = 0

    pinA9 = pyb.Pin(pyb.Pin.board.PA9, pyb.Pin.OUT_PP)
    timer1 = pyb.Timer(1, freq=50)
    t1ch2 = timer1.channel(2, pyb.Timer.PWM, pin=pinA9)
    aServo = Servo(t1ch2, angle=30, maxAngle=120)

    counter = 0

    yield

    while True:
        if state == 0:
            # Waiting for start
            if start.get():
                counter = 0
                state = 1
            yield
        elif state == 1:
            # Wait for fire
            if counter < 25:
                counter += 1
            else:
                if fire.get():
                    aServo.write(120)
                    fire.put(0)
                    state = 2
            yield
        elif state == 2:
            # Delay and reset
            if counter > 5:
                print("Done!")
                aServo.write(30)
                counter = 0
                start.put(0)
                hAngle.put(0)
                vAngle.put(45)
                readyForImage.put(0)
                state = 0
            else:
                counter += 1
            yield
        else:
            raise ValueError(f"Invalid Task 5 State: {state}")

if __name__ == "__main__":
    shareList = [
        task_share.Share("i", name="hAngle"),
        task_share.Share("b", name="start"),
        task_share.Share("b", name="ReadyForImage"),
        task_share.Share("i", name="vAngle"),
        task_share.Share("b", name="Fire")
    ]
    
    tasks = [
        cotask.Task(task1, name="Task 1", priority=2, period=10, shares=shareList),
        cotask.Task(task2, name="Task 2", priority=1, period=200, shares=shareList),
        cotask.Task(task3, name="Task 3", priority=0, period=100, shares=shareList),
        cotask.Task(task4, name="Task 4", priority=0, period=10, shares=shareList),
        cotask.Task(task5, name="Task 5", priority=0, period=200, shares=shareList),
    ]

    for task in tasks:
        cotask.task_list.append(task)

    while True:
        cotask.task_list.pri_sched()
