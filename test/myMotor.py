from motor import Motor
from time import sleep
from gpiozero.pins.native import NativeFactory

factory = NativeFactory()

motor = Motor(19, 26, active_high=False)

while True:
    motor.forward()
    print('forward')
    sleep(1)
    motor.stop()
    print('stop')
    sleep(1)
    motor.backward()
    print('backward')
    sleep(1)
    motor.stop()
    print('stop')
    sleep(1)

motor.close()
# del motor

# GPIO.cleanup()