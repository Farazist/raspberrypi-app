from gpiozero import DigitalOutputDevice
from threading import Timer
from utils.database import DataBase

class Motor:
    def __init__(self, name='', pin_factory=None):
        
        forward_port = int(DataBase.select(name + '_forward_port'))
        backward_port = int(DataBase.select(name + '_backward_port'))
        time = float(DataBase.select(name + '_time'))
        
        self.forward_motor = DigitalOutputDevice(pin=forward_port, active_high=False)
        self.backward_motor = DigitalOutputDevice(pin=backward_port, active_high=False)
        self.time = time
        self.name = name
        self.last_state = 'forward'
        print(self.name, 'ready')

    def forward(self, timer=False):
        self.backward_motor.off()
        self.forward_motor.on()
        self.last_state = 'forward'
        if timer:
            self.timer = Timer(self.time, self.stop)
            self.timer.start()
        print(self.name, 'forward')

    def backward(self, timer=False):
        self.forward_motor.off()
        self.backward_motor.on()
        if timer:
            self.timer = Timer(self.time, self.stop)
            self.timer.start()
        self.last_state = 'backward'
        print(self.name, 'backward')

    def stop(self):
        self.forward_motor.off()
        self.backward_motor.off()
        print(self.name, 'stop')
    
    def close(self):
        self.forward_motor.close()
        self.backward_motor.close()
        print(self.name, 'close')
