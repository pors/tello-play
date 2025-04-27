from djitellopy import tello
from time import sleep

me = tello.Tello(host='192.168.1.85')
#me = tello.Tello()
me.connect()
print(f"Bat: {me.get_battery()}")
print(f"Temp: {me.get_temperature()}")

# shut down the drone
me.end()
