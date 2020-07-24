from time import sleep
from gpiozero.pins.native import NativeFactory
from gpiozero import DigitalOutputDevice

factory = NativeFactory()

class Motor:
    def __init__(self, forward, backward, active_high=True, initial_value=False, pin_factory=None, name=''):
        self.forward_motor = DigitalOutputDevice(pin=forward, active_high=active_high)
        self.backward_motor = DigitalOutputDevice(pin=backward, active_high=active_high)
        self.name = name

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
motor = Motor(21, 24, active_high=False)

t = 2

while True:
    motor.forward()
    print('forward')
    sleep(t)
    motor.stop()
    print('stop')
    sleep(t)
    motor.backward()
    print('backward')
    sleep(t)
    motor.stop()
    print('stop')
    sleep(t)

motor.close()
# del motor

# GPIO.cleanup()