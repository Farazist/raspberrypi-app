# Farazist RaspberryPi App
App for smart recycle waste bottles
</br>
</br>
<img src="https://github.com/Farazist/farazist-raspberrypi-app/blob/master/images/raed_me/1.jpg" width="400">
<img src="https://github.com/Farazist/farazist-raspberrypi-app/blob/master/images/raed_me/2.jpg" width="400">
<img src="https://github.com/Farazist/farazist-raspberrypi-app/blob/master/images/raed_me/3.jpg" width="400">
<img src="https://github.com/Farazist/farazist-raspberrypi-app/blob/master/images/raed_me/4.jpg" width="400">
## Resources
The mobile application of FARAZIST is available via the following link:
* https://cafebazaar.ir/app/ir.farazist.farazist_app
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

| Name | Pin # | Pin name   |
|:------:|:-------:|:------------:|
| SDA  | 24    | GPIO8      |
| SCK  | 23    | GPIO11     |
| MOSI | 19    | GPIO10     |
| MISO | 21    | GPIO9      |
| IRQ  | None  | None       |
| GND  | Any   | Any Ground |
| RST  | 22    | GPIO25     |
| 3.3V | 1     | 3V3        |

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
## Install font on raspbian
* Download the font
* Extract the downloaded font file in command line (we extract it in the Downloads folder)
* Open a terminal and run the following codes:
  * cd ~/Downloads/
  * cp *.otf ~/.fonts/
  * cp *.ttf ~/.fonts/
  * fc-cache -v -f

## Status
This project is early in development and does not yet have a stable API.
  
