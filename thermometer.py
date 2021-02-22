""" Based on https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
"""
import time
import board
import adafruit_dht
import sqlite3
import config
import logging
import gpiozero
from gpiozero.pins.rpigpio import RPiGPIOFactory

LOGFILE = "temperature.log"

logging.basicConfig(filename=LOGFILE, level=logging.INFO)
#logging.basicConfig(level=logging.INFO)
print("Logging to " + LOGFILE)

def get_power_pin(config):
    powerPin = config.getint('thermo', 'PowerPin', fallback=-1)
    if powerPin != -1:
        return gpiozero.pins.rpigpio.RPiGPIOPin(RPiGPIOFactory(),22)
    else:
        return None

def power_switch(pin, state):
    if pin:
        pin.output_with_state(state)

#  hello, IT
def have_you_tried_turning_it_off_and_on_again(pin):
    logging.warning("Turn OFF then turn ON the DHT sensor")
    power_switch(pin, 0)
    time.sleep(3)
    power_switch(pin, 1)

conf = config.init()

powerPin = get_power_pin(conf)
power_switch(powerPin, 1)

# Initiate the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

dbPath = conf.get('app', 'PathToDatabase')

conn = sqlite3.connect(dbPath)
with conn:
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS DHT_data (timestamp DATETIME, temp NUMERIC, hum NUMERIC)")

    # you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
    # This may be necessary on a Linux single board computer like the Raspberry Pi,
    # but it will not work in CircuitPython.
    # dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

    # Default sleep before retry in case of exception. After continous errors we'll increase that.
    sleepException = 3.0
    sensor_not_found = 0
    while True:
        try:
            # Print the values to the serial port
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            logging.info(time.strftime("%Y-%m-%d %H:%M:%S, ")
                         + "Temp: {:.1f} C,    Humidity: {}% ".format(temperature_c, humidity))
            cur.execute("INSERT INTO DHT_data values(datetime('now'), (?), (?))", (temperature_c, humidity))
            conn.commit()

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            logging.warning(time.strftime("%Y-%m-%d %H:%M:%S ") + error.args[0])
            time.sleep(sleepException)
            sleepException *= 2
            if "DHT sensor not found" in error.args[0]:
                sensor_not_found += 1
                if sensor_not_found == 3:
                    have_you_tried_turning_it_off_and_on_again(powerPin)
            else:
                sensor_not_found = 0
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(45)
        sleepException = 3.0
        sensor_not_found = 0
