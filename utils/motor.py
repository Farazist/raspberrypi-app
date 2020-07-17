from gpiozero import DigitalOutputDevice

class Motor:
    def __init__(self, forward, backward, active_high=True, initial_value=False, pin_factory=None, name=''):
        self.forward_motor = DigitalOutputDevice(pin=forward, active_high=active_high)
        self.backward_motor = DigitalOutputDevice(pin=backward, active_high=active_high)
        self.name = name
        print(self.name, 'ready')

    def forward(self):
        self.forward_motor.on()
        self.backward_motor.off()
        print(self.name, 'forward')

    def backward(self):
        self.forward_motor.off()
        self.backward_motor.on()
        print(self.name, 'backward')

    def stop(self):
        self.forward_motor.off()
        self.backward_motor.off()
        print(self.name, 'stop')
    
    def close(self):
        self.forward_motor.close()
        self.backward_motor.close()
        print(self.name, 'close')
