import pyb
import cotask
import task_share
import motor_driver
import encoder_reader
import controller
import utime


def task1(shares):
    """!
    This task handles turning the panning axis of the turret
    @param shares A tuple of shared variables between tasks
    @returns None
    """
    (set_point, triggered) = shares

    state = 0

    pinC1 = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
    pinA0 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP) 
    pinA1 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_PP) 
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)
    tim5 = pyb.Timer(5, freq=20000)
    tim8 = pyb.Timer(8, prescaler=1, period=65535)
    motor = motor_driver.MotorDriver(pinC1, pinA0, pinA1, tim5)
    encoder = encoder_reader.Encoder(pinC6, pinC7, tim8)
    ctrl = controller.Controller(encoder, motor, 8000, 1/16)

    while True:
        if state == 0:
            # Init
            state = 1
            yield
        elif state == 1:
            # Waiting for Trigger
            if triggered.get():
                set_point.put(4000)
                ctrl.set_setpoint(set_point.get())
                state = 3
            yield
        elif state == 2:
            # Idle
            if set_point.get() != ctrl.setpoint:
                ctrl.set_setpoint(set_point.get())
                state = 3
            yield
        elif state == 3:
            # Panning
            if set_point.get() == ctrl.setpoint:
                state = 2
            yield
        else:
            raise ValueError(f"Invalid Task 1 State: {state}")

def task2(shares):
    """!
    This task handles the start trigger button
    @param shares A tuple of shared variables between tasks
    @returns None
    """
    (set_point, triggered) = shares

    state = 0

    pinB0 = pyb.Pin(pyb.Pin.board.PB0, pyb.Pin.IN, pull=pyb.Pin.PULL_UP)

    while True:
        if state == 0:
            # Init
            triggered.put(0)
            state = 1
            yield
        elif state == 1:
            # Waiting
            if not pinB0.read():
                triggered.put(1)
                state = 2
            yield 
        elif state == 2:
            # Triggered
            yield
        else:
            raise ValueError(f"Invalid Task 2 State: {state}")

def task3(shares):
    """!
    This task handles turning the vertical axis of the turret
    @param shares A tuple of shared variables between tasks
    @returns None
    """
    (set_point, triggered) = shares

    state = 0

    pinA2 = pyb.Pin(pyb.Pin.board.PA2, pyb.Pin.OUT_PP)

    while True:
        if state == 0:
            # Init
            state = 1
            yield
        elif state == 1:
            # Idle
            yield 
        elif state == 2:
            # Turning
            yield
        else:
            raise ValueError(f"Invalid Task 3 State: {state}")