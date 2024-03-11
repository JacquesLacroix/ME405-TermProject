import pyb
import cotask
import task_share
import utime
from motor_driver import MotorDriver
from encoder_reader import Encoder
from controller import Controller
from servo import Servo
from mlx_cam import MLX_Cam

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

    pinC1 = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
    pinA0 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP)
    pinA1 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_PP) 
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)
    tim5 = pyb.Timer(5, freq=20000)
    tim8 = pyb.Timer(8, prescaler=1, period=65535)
    motor = MotorDriver(pinC1, pinA0, pinA1, tim5)
    encoder = Encoder(pinC6, pinC7, tim8)
    ctrl = Controller(encoder, motor, Controller.angleToTicks(hAngle.get()), 0.4, 8000, 4)

    yield

    while True:
        if state == 0:
            # Waiting for start
            if start.get():
                hAngle.put(180)
                ctrl.setAngle(hAngle.get())
                state = 2
            yield
        elif state == 1:
            # Idle
            if hAngle.get() != ctrl.readAngle():
                ctrl.setAngle(hAngle.get())
                readyForImage.put(0)
                state = 2
            yield
        elif state == 2:
            # Panning
            ctrl.run()
            if hAngle.get() == ctrl.readAngle():
                readyForImage.put(1)
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

    ser = pyb.USB_VCP()

    yield

    while True:
        if state == 0:
            # Waiting
            if ser.any():
                try:
                    line = ser.readline()
                    if "Begin" in line:
                        start.put(1)
                        state = 1
                except:
                    pass
            yield 
        elif state == 1:
            # Start
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

    pinA10 = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
    timer1 = pyb.Timer(1, freq=50)
    t1ch3 = timer1.channel(3, pyb.board.PWM, pin=pinA10)
    vServo = Servo(t1ch3, angle=vAngle.get())

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
        else:
            raise ValueError(f"Invalid Task 3 State: {state}")

def task4(shares):
    """!
    This task handles taking images and setting angles
    @param shares A tuple of shared variables between tasks
    @returns None
    """
    (hAngle, start, readyForImage, vAngle, fire) = shares

    fire.put(0)

    pinB8 = pyb.Pin(pyb.Pin.board.PB8, pyb.Pin.ALT, alt=4)
    pinB9 = pyb.Pin(pyb.Pin.board.PB9, pyb.Pin.ALT, alt=4)
    i2c = pyb.I2C(1, pyb.I2C.CONTROLLER, baudrate=100000)
    camera = MLX_Cam(i2c)
    image = None
    arrayImage = []
    vMax = 0
    hMax = 0

    yield

    while True:
        if readyForImage.get():
            while not image:
                image = camera.get_image_nonblocking()
                yield
            for line in camera.get_csv(image):
                arrayImage.append(line.split(","))
                yield

            # Apply blur here

            for (vIdx, line) in enumerate(arrayImage):
                for (hIdx, pixel) in enumerate(line):
                    if pixel > arrayImage[vMax][hMax]:
                        vMax = vIdx
                        hMax = hIdx
                yield

            hNew = hAngle.get() + hIdx - 16
            vNew = vIdx

            if hNew == hAngle.get() and vNew == vAngle.get():
                fire.put(1)
            else:
                hAngle.put(hNew)
                vAngle.put(vNew)
            
            image = None
            arrayImage = []
            vMax = 0
            hMax = 0
            yield

def task5(shares):
    """!
    This task handles actutating the trigger
    @param shares A tuple of shared variables between tasks
    @returns None
    """
    (hAngle, start, readyForImage, vAngle, fire) = shares

    state = 0

    pinA8 = pyb.Pin(pyb.Pin.board.PA8, pyb.Pin.OUT_PP)
    t1ch1 = timer1.channel(1, pyb.board.PWM, pin=pinA8)
    aServo = Servo(t1ch1, angle=0)

    counter = 0

    yield

    while True:
        if state == 0:
            # Waiting for Trigger
            if start.get():
                state = 1
            yield
        elif state == 1:
            # Wait for Fire
            if fire.get():
                aServo.write(90)
                fire.put(0)
                state = 2
            yield
        elif state == 2:
            # Delay and reset
            if counter > 10:
                aServo.write(0)
                counter = 0
                state = 1
            else:
                counter += 1
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
        cotask.Task(task1, name="Task 1", priority=2, period=30, shares=shareList),
        cotask.Task(task2, name="Task 2", priority=1, period=200, shares=shareList),
        cotask.Task(task3, name="Task 3", priority=0, period=100, shares=shareList),
        cotask.Task(task4, name="Task 4", priority=0, period=100, shares=shareList),
        cotask.Task(task5, name="Task 5", priority=0, period=100, shares=shareList),
    ]

    for task in tasks:
        cotask.task_list.append(task)

    while True:
        cotask.task_list.pri_sched()