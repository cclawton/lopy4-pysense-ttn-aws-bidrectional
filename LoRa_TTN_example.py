import binascii
import pycom
import socket
import time
from network import LoRa
from pysense import Pysense
from MPL3115A2 import MPL3115A2


# Colors
off = 0x000000
red = 0xff0000
green = 0x00ff00
blue = 0x0000ff
#colors = ["off", "red", "green", "blue"]
colors = [off, red, green, blue]

# Turn off hearbeat LED
pycom.heartbeat(False)

# Initialize LoRaWAN radio
#lora = LoRa(mode=LoRa.LORAWAN)
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AU915, adr=False, tx_retries=0, device_class=LoRa.CLASS_A)

# Set network keys
app_eui = binascii.unhexlify('70B3D57ED000EF92')
app_key = binascii.unhexlify('47D97E33D867DA5ACFE358F7BD75522B')

# remove some channels
for i in range(16, 65):
    lora.remove_channel(i)
for i in range(66, 72):
    lora.remove_channel(i)

# Join the network
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
pycom.rgbled(red)

# init the libraries
py = Pysense()
temp = MPL3115A2()

# Loop until joined
while not lora.has_joined():
    print('Not joined yet...')
    pycom.rgbled(off)
    time.sleep(0.1)
    pycom.rgbled(red)
    time.sleep(2)

print('Joined')
pycom.rgbled(blue)

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setblocking(False)
colorindex = 3

while True:
    # Read data from the libraries and place into string
    #data = "%d" % (temp.temperature() * 100)
    data = temp.temperature()
    print("Sending %.5s" % data)
    data = int (data * 100);
    # send the data over LPWAN network
    s.send(bytes([int(data / 256), data % 256, colorindex   ]))
    s.settimeout(3.0) # configure a timeout value of 3 seconds
    try:
        rx_pkt = s.recv(64)   # get the packet received (if any)
        print(rx_pkt)
        colorindex = int.from_bytes(rx_pkt, "big")
    except socket.timeout:
        print('No packet received')

    pycom.rgbled(green)
    time.sleep(0.1)
    pycom.rgbled(colors[colorindex])
    time.sleep(29.9)
