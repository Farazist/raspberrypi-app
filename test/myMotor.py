from gpiozero import Motor
import RPi.GPIO as GPIO
from time import sleep

motor = Motor(forward=27, backward=4)

# while True:
motor.forward()
sleep(5)
motor.stop()
sleep(10)
motor.backward()
sleep(5)
motor.stop()
sleep(10)

# del motor

GPIO.cleanup()