# raspberrypi-app
App for smart recycle waste bottles
</br>
</br>
<img src="https://github.com/Farazist/farazist-raspberrypi-app/blob/master/images/raed_me/1.jpg" width="400">
<img src="https://github.com/Farazist/farazist-raspberrypi-app/blob/master/images/raed_me/2.jpg" width="400">
<img src="https://github.com/Farazist/farazist-raspberrypi-app/blob/master/images/raed_me/3.jpg" width="400">
<img src="https://github.com/Farazist/farazist-raspberrypi-app/blob/master/images/raed_me/4.jpg" width="400">

## Requirements
* Raspberry Pi OS (32-bit)
* Python 3.7
* Required
  * TensorFlow Lite
  * PySide2
  * scipy
  * gpiozero
  * qrcode
  * sqlite3
  * escpos
  * qtquick
## Hardware requirements
 * Raspberry Pi 4 (model B - 4GB RAM)
 * Raspberry Pi NoIR Camera V2
 
### Setup RFID (mfrc522 module)
* GPIO pins:
    * RST: 25
    * MISO: 9
    * MOSI: 10
    * SCK: 11
    * SDA: 8
* commands:

```
lsmod | grep spi
```
```
sudo pip3 install spidev
```
```
sudo pip3 install mfrc522
```
 
## Status
This project is early in development and does not yet have a stable API.
  
