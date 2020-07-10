from tkinter import *
from time import sleep
from functools import partial
from gpiozero.pins.native import NativeFactory
from gpiozero import LED

factory = NativeFactory()

pins = [2,3,4,7, 8, 14, 15 ,25]

leds = [{'pin_number': pin, 'flag': False , 'led': LED(pin, pin_factory=factory)} for pin in pins]

def func(i):
    global led1_flag

    if leds[i]['flag'] == False:
        lbls[i].configure(text='ON')
        leds[i]['flag'] = True
        leds[i]['led'].on()
    else:
        lbls[i].configure(text='OFF')
        leds[i]['flag'] = False
        leds[i]['led'].off()
        
window = Tk()
window.title("GPIO Test")
# window.geometry('350x200')
 
lbls = []
for i in range(len(pins)):
    lbls.append(Label(window, text="OFF"))
    lbls[i].grid(column=0, row=i)

btns = []
for i in range(len(pins)):
    btn = Button(window, text="PIN " + str(pins[i]), command=partial(func, i), height = 3, width = 5)
    btn.grid(column=1, row=i)
    btns.append(btn)
    
window.mainloop()