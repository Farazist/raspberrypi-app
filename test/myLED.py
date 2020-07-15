from gpiozero import LED
from time import sleep

red = LED(19)

# while True:

red.on()
print('on')
sleep(4)

red.off()
print('off')
sleep(4)