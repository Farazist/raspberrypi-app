from gpiozero import *
from time import sleep

class GPIO:
    
    

led = LED(8)
button = Button(7)

while True:

    if button.is_pressed:
        print("Pressed")
    else:
        print("Released")

    led.on()
    sleep(1)
    led.off()
    sleep(1)
