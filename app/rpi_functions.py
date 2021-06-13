from gpiozero import LED, Button
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085
from threading import Thread, Event
from config import DEBUG
import subprocess

'''
Python file containing code that only runs on raspberry pi hardware
'''

def reboot():
	global blinkingled, loggingled
	print('rebooting')
	command = "/usr/bin/sudo /sbin/shutdown -r now"
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print(output)
	blinkingled.off()
	loggingled.off()
	exit(0)
	
# thread termination event
terminateEvent = Event()

# logging LED
loggingled = LED(18)
loggingled.on()

# blinking LED
blinkingled = LED(27)
blinkingled.blink(on_time=0.25, off_time=1, background=True)

# reboot button
rebootbtn = Button(17)
rebootbtn.when_pressed = reboot

# initialize BMP180 sensor
# loop until the sensor is properly connected and detected
sensor = None
while sensor is None:
    try:
        sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)
    except OSError:
        if DEBUG: print("Cannot initialize BMP180 sensor")

# define DHT sensor type and pin
dsensor = Adafruit_DHT.DHT11
pin = 4

# read BMP180 sensor
def BMP180read():
    bmp_temperature, pressure = None, None
    while bmp_temperature is None or pressure is None:
        try:
            bmp_temperature, pressure = sensor.read_temperature(), sensor.read_pressure()
        except OSError:
            if DEBUG: print("Cannot read BMP180 sensor")
        except NameError:
            if DEBUG: print("BMP180 sensor not initialized, please check your sensor wiring.")
    return bmp_temperature, pressure

# read DHT11 sensor
def DHT11read():
    instTemperature, instHumidity = None, None
    while instHumidity is None or instTemperature is None:
        instHumidity, instTemperature = Adafruit_DHT.read(dsensor, pin)
        if instHumidity is None or instTemperature is None:
            if DEBUG: print("Faulty DHT11 reading")
        else:
            humidity, temperature = instHumidity, instTemperature
            if DEBUG: print("Good DHT11 reading")
    return instTemperature, instHumidity
