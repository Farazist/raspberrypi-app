from gpiozero import DistanceSensor, LED
from signal import pause

def in_range():
    print('In range')

def out_of_range():
    print('Out of range')


sensor = DistanceSensor(20, 21, max_distance=1, threshold_distance=0.2)

sensor.when_in_range = in_range
sensor.when_out_of_range = out_of_range

pause()