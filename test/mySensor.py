from gpiozero import DistanceSensor, LED
from signal import pause

def test():
    print('test')

sensor = DistanceSensor(15, 14, max_distance=1, threshold_distance=0.2)

sensor.when_in_range = test

pause()