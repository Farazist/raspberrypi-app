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
motor = Motor(23, 18, active_high=False)

t = 5

motor.stop()
print('stop')
sleep(t * 2)

while True:
    motor.forward()
    print('forward')
    sleep(t)
    motor.stop()
    print('stop')
    sleep(t * 2)
    motor.backward()
    print('backward')
    sleep(t)
    motor.stop()
    print('stop')
    sleep(t * 2)

motor.close()
# del motor

# GPIO.cleanup()