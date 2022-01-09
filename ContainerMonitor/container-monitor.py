import I2C_LCD_driver_UBUNTU as driver
import RPi.GPIO as gpio
import os, json, docker
from time import sleep

# make config directory
try:
    os.mkdir("config")
except:
    pass

# default variables
showAll = True
conatiners = []
delay = 10

lcd = driver.lcd()          # initialize lcd driver
client = docker.from_env()  # initialize docker client

gpio.setmode(gpio.BCM)      # set gpio label to BCM

# define led pins
indicators = [6, 13, 19, 26]

# set gpio pins as outputs
for i in indicators:
    gpio.setup(i, gpio.OUT)

# define custom characters
fontdata = [
    # char(0) - Running symbol
    [
        0b00000,
        0b01110,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b01110,
        0b00000
    ],
    # char(1) - Exited symbol
    [
        0b00000,
        0b01110,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
        0b01110,
        0b00000
    ],
    # char(2) - Paused symbol
    [
        0b00000,
        0b01110,
        0b10101,
        0b10101,
        0b10101,
        0b10101,
        0b01110,
        0b00000
    ],
    # char(3) - Restarting symbol
    [
        0b00000,
        0b01110,
        0b10001,
        0b11101,
        0b10111,
        0b10001,
        0b01110,
        0b00000
    ],
    # char(4) - Unknown symbol
    [
        0b00000,
        0b01110,
        0b10011,
        0b10101,
        0b10101,
        0b11001,
        0b01110,
        0b00000
    ]
]

# load custom characters
lcd.lcd_load_custom_chars(fontdata)

# function to send a string depending on the status
def statusStr(status):
    if status ==  "running":
        return "RUN"
    elif status ==  "exited":
        return "STP"
    elif status ==  "paused":
        return "PAU"
    elif status ==  "restarting":
        return "RES"
    return "UNK"

# function to write a character on the lcd depending on the status
def statusSymbol(status):
    if status ==  "running":
        return 0
    elif status ==  "exited":
        return 1
    elif status ==  "paused":
        return 2
    elif status ==  "restarting":
        return 3
    return 4

# function to update the lcd content
def updateLCD(status):
    # clear the lcd
    lcd.lcd_clear()
    # turn off the lcds
    for i in indicators:
        gpio.output(i, False)
    for i in range(len(status)):
        # print the status on the console and the lcd
        print(status[i])
        # update line 1
        lcd.lcd_print(status[i][0], i+1, 0)
        lcd.lcd_write_char(statusSymbol(status[i][1]))
        gpio.output(indicators[i], True if status[i][1] == "running" else False)
    return

# show initial message
lcd.lcd_clear()
motd = """\
+------------------+
|    CONTAINER     |
|     MONITOR      |
+------------------+
"""
print(motd)
lcd.lcd_print("+------------------+", 1)
lcd.lcd_print("|    CONTAINER     |", 2)
lcd.lcd_print("|     MONITOR      |", 3)
lcd.lcd_print("+------------------+", 4)
sleep(5)
lcd.lcd_clear()

# load config file
print("Loading configuration file...")
while True:
    try:
        with open("config/config.json", "rt") as f:
            content = json.loads(f.read())
        showAll = content["show-all"]
        containers = content["containers"]
        delay = content["delay"]
        print("Configuration loaded!")
        break
    except FileNotFoundError:
        print("Configuration file not found or unusable. Creating it...")
        with open("config/config.json", "wt") as f:
            f.write(json.dumps({"show-all":True, "containers":[], "delay":10}, indent=4))

# main loop
while True:
    print()
    if showAll:
        # get all containers
        containerList = client.containers.list(all=True)
    elif not showAll and containers:
        # get the specified containers
        containerList = []
        for x in containers:
            try:
                containerList.append(client.containers.get(x))
            except:
                pass
    
    # separate the containers in chunks of 4 each
    containerList = [containerList[i:i+4] for i in range(0, len(containerList), 4)]
    for container in containerList:
        # build the strings to be showned
        status = []
        for c in container:
            status.append([c.name[:12].ljust(12, " ") + " | " + statusStr(c.status) + " ", c.status])
        updateLCD(status)
        sleep(delay)