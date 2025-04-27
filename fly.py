from djitellopy import tello
from time import sleep

# t = tello.Tello() # AP mode
t = tello.Tello(host="192.168.1.85")

t.connect()

print(f"Bat: {t.get_battery()}")
print(f"Temp: {t.get_temperature()}")

t.takeoff()

"""Send RC control via four channels. Command is sent every self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
Arguments:
    left_right_velocity: -100~100 (left/right)
    forward_backward_velocity: -100~100 (forward/backward)
    up_down_velocity: -100~100 (up/down)
    yaw_velocity: -100~100 (yaw)
"""
t.send_rc_control(0, 50, 0, 0)
sleep(2)
t.send_rc_control(30, 0, 0, 0)
sleep(2)
t.send_rc_control(0, 0, 0, 0)

t.land()
