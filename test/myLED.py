from gpiozero import LED
from time import sleep

red = LED(21, active_high=False)

# while True:

red.on()
print('on')
sleep(30)

# red.off()
# print('off')
# sleep(4)