'''
dummy python file for running tests without a Raspberry Pi
'''
statusled=1

# read BMP180 sensor
def BMP180read():
    bmp_temperature, pressure = 30, 100120
    return bmp_temperature, pressure

# read DHT11 sensor
def DHT11read():
    instTemperature, instHumidity = 30, 85
    return instTemperature, instHumidity

# flash the status LED
def flashStatusLED(led, duration):
    pass
