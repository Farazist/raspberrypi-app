from gpiozero import Motor
import RPi.GPIO as GPIO
from time import sleep

motor = Motor(forward=13, backward=26)

# while True:
motor.forward()
sleep(0.25)
motor.stop()
sleep(2)
motor.backward()
sleep(0.25)
motor.stop()
sleep(2)

del motor

GPIO.cleanup()