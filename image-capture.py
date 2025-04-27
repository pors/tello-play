from djitellopy import tello
from time import sleep
import cv2

me = tello.Tello(host="192.168.1.85")
# me = tello.Tello()
me.connect()
print(me.get_battery())
print(f"Temp: {me.get_temperature()}")

# me.turn_motor_off()
print(me.get_current_state())

me.streamon()

while True:
    frame = me.get_frame_read().frame
    # Process the frame (e.g., display it, save it, etc.)
    # For demonstration, we'll just print the shape of the frame
    print(frame.shape)
    frame = cv2.resize(frame, (360, 240))
    cv2.imshow("Frame", frame)
    # Check if the "q" key is pressed to exit the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

me.streamoff()

