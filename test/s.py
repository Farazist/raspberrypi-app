from time import sleep
from gpiozero.pins.native import NativeFactory
from gpiozero import DigitalOutputDevice

factory = NativeFactory()

class Motor:
    def __init__(self, forward, backward, active_high=True, initial_value=False, pin_factory=None):
        self.forward_motor = DigitalOutputDevice(pin=forward, active_high=active_high)
        self.backward_motor = DigitalOutputDevice(pin=backward, active_high=active_high)

    def forward(self):
        self.forward_motor.on()
        self.backward_motor.off()

    def backward(self):
        self.forward_motor.off()
        self.backward_motor.on()

    def stop(self):
        self.forward_motor.off()
        self.backward_motor.off()
    
    def close(self):
        self.forward_motor.close()
        self.backward_motor.close()
motor = Motor(12, 16, active_high=True)

t = 0.25

while True:
    motor.forward()
    print('forward')
    sleep(t)
    motor.stop()
    print('stop')
    sleep(t * 6)
    motor.backward()
    print('backward')
    sleep(t)
    motor.stop()
    print('stop')
    sleep(t * 6)

motor.close()
# del motor

# GPIO.cleanup()