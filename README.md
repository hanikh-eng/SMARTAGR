sudo apt-get install python3-rpi.gpio 
*** For the gpio ***


sudo apt-get install python3-smbus i2c-tools

sudo raspi-config
# Interface Options > I2C > Enable

i2cdetect -y 1 **#** to check if the PCF8591 is connected

*** Connect the PCF8591 to potentiometre into your Raspberry Pi 5: ***

Wiring Overview
VCC → 3.3V or 5V on Pi

GND → GND

SDA → SDA on Pi (GPIO 2 / Pin 3)

SCL → SCL on Pi (GPIO 3 / Pin 5)

Potentiometer middle pin (wiper) → AIN0 (pin 1 on PCF8591)

Other potentiometer pins → VCC and GND


*** ACTIONEUR PINOUT into your Raspberry Pi 5: ***

"HEATING": LED(17)
"WATERING": LED(27)
"HUMIDIFIER": LED(22)
"WATER_PUMP": LED(5)
"LIGHTNING": LED(6)