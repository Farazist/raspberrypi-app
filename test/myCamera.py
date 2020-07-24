from picamera import PiCamera
from time import sleep

camera = PiCamera()
#camera.rotation = 180
camera.resolution = (2592, 1944)
camera.framerate = 15
#camera.exposure_mode = 'beach'
#camera.awb_mode = 'sunlight'
camera.start_preview()
#camera.start_preview(fullscreen=False, window = (100, 20, 640, 480))
sleep(60)
camera.capture('/home/pi/Desktop/image.jpg')
camera.stop_preview()