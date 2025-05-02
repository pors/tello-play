import threading
import asyncio
import time
from bleak import BleakClient, BleakScanner

# The characteristic we want to read. This is the same for all GameSir T1d controllers.
# The UUID is a standard Bluetooth GATT characteristic for HID devices.
CHARACTERISTIC_UUID = "00008651-0000-1000-8000-00805f9b34fb"

class GameSirT1d:
    """Raw GameSir T1d controller interface."""

    def __init__(self):
        # Joystick values (0-1023, with 512 as center)
        self.lx = 512
        self.ly = 512
        self.rx = 512
        self.ry = 512

        # Analog triggers (0-255)
        self.l2 = 0
        self.r2 = 0

        # Digital buttons (0 or 1)
        self.a = 0
        self.b = 0
        self.x = 0
        self.y = 0
        self.l1 = 0
        self.r1 = 0
        self.c1 = 0
        self.c2 = 0
        self.menu = 0

        # D-pad
        self.dpad_up = 0
        self.dpad_down = 0
        self.dpad_left = 0
        self.dpad_right = 0

        # Connection state
        self.connected = False
        self._client = None

    def parse_data(self, data):
        """Parse the raw data from the controller"""
        if len(data) < 12:
            return False

        # Parse joysticks
        self.lx = ((data[2]) << 2) | (data[3] >> 6)
        self.ly = ((data[3] & 0x3F) << 4) + (data[4] >> 4)
        self.rx = ((data[4] & 0xF) << 6) | (data[5] >> 2)
        self.ry = ((data[5] & 0x3) << 8) + ((data[6]))

        # Parse triggers
        self.l2 = data[7]
        self.r2 = data[8]

        # Parse buttons from byte 9
        buttons = data[9]
        self.a = int(bool(buttons & 0x01))
        self.b = int(bool(buttons & 0x02))
        self.menu = int(bool(buttons & 0x04))
        self.x = int(bool(buttons & 0x08))
        self.y = int(bool(buttons & 0x10))
        self.l1 = int(bool(buttons & 0x40))
        self.r1 = int(bool(buttons & 0x80))

        # Parse more buttons from byte 10
        buttons2 = data[10]
        self.c1 = int(bool(buttons2 & 0x04))
        self.c2 = int(bool(buttons2 & 0x08))

        # Parse D-pad from byte 11
        dpad = data[11]
        self.dpad_up = int(dpad == 0x01)
        self.dpad_right = int(dpad == 0x03)
        self.dpad_down = int(dpad == 0x05)
        self.dpad_left = int(dpad == 0x07)

        return True

    def __str__(self):
        """Return a string representation of the controller state"""
        return (
            f"Joysticks: LX={self.lx}, LY={self.ly}, RX={self.rx}, RY={self.ry}\n"
            f"Triggers: L2={self.l2}, R2={self.r2}\n"
            f"Buttons: A={self.a}, B={self.b}, X={self.x}, Y={self.y}, "
            f"L1={self.l1}, R1={self.r1}, C1={self.c1}, C2={self.c2}, Menu={self.menu}\n"
            f"D-pad: Up={self.dpad_up}, Down={self.dpad_down}, Left={self.dpad_left}, Right={self.dpad_right}"
        )

    def get_left_stick(self):
        """Get normalized values for left stick (-1.0 to 1.0)"""
        x = (self.lx - 512) / 512  # -1.0 to 1.0
        y = (self.ly - 512) / 512  # -1.0 to 1.0
        return (x, y)

    def get_right_stick(self):
        """Get normalized values for right stick (-1.0 to 1.0)"""
        x = (self.rx - 512) / 512  # -1.0 to 1.0
        y = (self.ry - 512) / 512  # -1.0 to 1.0
        return (x, y)


class GameSirT1dPygame:
    """A pygame-compatible wrapper for the GameSir T1d controller with reconnection logic."""

    def __init__(self, controller_name, max_reconnect_attempts=5):
        self.controller_name = controller_name
        self._initialized = False
        self._running = False
        self._thread = None
        self._max_reconnect_attempts = max_reconnect_attempts
        self._reconnect_delay = 2.0  # seconds between reconnection attempts

        # Connection status tracking
        self._connection_state = (
            "disconnected"  # "disconnected", "connecting", "connected"
        )
        self._last_connect_attempt = 0
        self._connect_attempts = 0

        # Controller state
        self._axes = [0.0] * 4  # LX, LY, RX, RY
        self._buttons = [0] * 12  # All buttons
        self._hat = (0, 0)  # D-pad

        # Underlying controller instance
        self._controller = GameSirT1d()

    def init(self):
        """Initialize the joystick. This must be called before any other method."""
        if self._initialized:
            return True

        # Start the BLE thread
        self._running = True
        self._thread = threading.Thread(target=self._ble_thread)
        self._thread.daemon = True
        self._thread.start()

        # Wait for initialization to complete
        timeout = 10  # seconds
        start_time = time.time()
        while not self._initialized and time.time() - start_time < timeout:
            time.sleep(0.1)

        return self._initialized

    def _ble_thread(self):
        """Background thread that handles BLE communication."""
        try:
            # Create and run the asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._ble_task())
        except Exception as e:
            print(f"BLE thread error: {e}")
        finally:
            self._running = False
            self._connection_state = "disconnected"

    async def _ble_task(self):
        """Asynchronous task to handle BLE communication with reconnection logic."""
        while self._running:
            try:
                # Only try to reconnect if we're not already connected or connecting
                if self._connection_state == "disconnected":
                    self._connection_state = "connecting"
                    print(f"Scanning for {self.controller_name}...")

                    # Find the controller
                    device = await BleakScanner.find_device_by_name(
                        self.controller_name
                    )

                    if not device:
                        self._connect_attempts += 1
                        print(
                            f"Could not find {self.controller_name}. Is it turned on? (Attempt {self._connect_attempts}/{self._max_reconnect_attempts})"
                        )

                        if self._connect_attempts >= self._max_reconnect_attempts:
                            print("Maximum reconnection attempts reached. Giving up.")
                            break

                        self._connection_state = "disconnected"
                        await asyncio.sleep(self._reconnect_delay)
                        continue

                    print(f"Found {self.controller_name} at {device.address}")
                    print("Connecting...")

                    # Connect to the controller
                    async with BleakClient(device.address, timeout=5.0) as client:
                        print("Connected!")
                        self._initialized = True
                        self._connection_state = "connected"
                        self._connect_attempts = (
                            0  # Reset attempt counter on successful connection
                        )

                        # Main polling loop
                        while self._running and self._connection_state == "connected":
                            try:
                                # Read controller state
                                data = await client.read_gatt_char(CHARACTERISTIC_UUID)

                                # Parse data
                                if self._controller.parse_data(data):
                                    # Update our state
                                    self._update_state()

                                # Poll at a reasonable rate (20Hz)
                                await asyncio.sleep(0.05)
                            except Exception as e:
                                print(f"Error reading controller: {e}")
                                print(
                                    "Connection may have been lost. Attempting to reconnect..."
                                )
                                self._connection_state = "disconnected"
                                break

                # If we exit the connection block, wait before trying to reconnect
                await asyncio.sleep(self._reconnect_delay)

            except Exception as e:
                print(f"BLE connection error: {e}")
                print("Will try to reconnect...")
                self._connection_state = "disconnected"
                await asyncio.sleep(self._reconnect_delay)

    def _update_state(self):
        """Update the pygame-compatible state from the controller data."""
        # Same as before, no changes needed
        # Update axes (already normalized to -1.0 to 1.0)
        left_x, left_y = self._controller.get_left_stick()
        right_x, right_y = self._controller.get_right_stick()

        self._axes[0] = left_x
        self._axes[1] = left_y
        self._axes[2] = right_x
        self._axes[3] = right_y

        # Update buttons
        self._buttons[0] = self._controller.a
        self._buttons[1] = self._controller.b
        self._buttons[2] = self._controller.x
        self._buttons[3] = self._controller.y
        self._buttons[4] = self._controller.l1
        self._buttons[5] = self._controller.r1
        self._buttons[6] = (
            1 if self._controller.l2 > 127 else 0
        )  # Convert analog to digital
        self._buttons[7] = (
            1 if self._controller.r2 > 127 else 0
        )  # Convert analog to digital
        self._buttons[8] = self._controller.c1
        self._buttons[9] = self._controller.start
        self._buttons[10] = self._controller.menu

        # Update hat (D-pad)
        hat_x, hat_y = 0, 0
        if self._controller.dpad_left:
            hat_x = -1
        elif self._controller.dpad_right:
            hat_x = 1
        if self._controller.dpad_up:
            hat_y = -1
        elif self._controller.dpad_down:
            hat_y = 1
        self._hat = (hat_x, hat_y)

    # Status methods for connection state

    def is_connected(self):
        """Return True if the controller is currently connected."""
        return self._connection_state == "connected"

    def get_connection_state(self):
        """Return the current connection state."""
        return self._connection_state

    # Pygame-compatible interface methods (same as before)

    def get_init(self):
        """Return True if the joystick is initialized."""
        return self._initialized

    def get_id(self):
        """Get the joystick ID number."""
        return 0

    def get_name(self):
        """Return the name of the joystick."""
        return self.controller_name

    def get_numaxes(self):
        """Return the number of axes on the joystick."""
        return len(self._axes)

    def get_axis(self, axis_number):
        """Get the current position of the given axis."""
        if 0 <= axis_number < len(self._axes):
            return self._axes[axis_number]
        return 0.0

    def get_numbuttons(self):
        """Return the number of buttons on the joystick."""
        return len(self._buttons)

    def get_button(self, button_number):
        """Get the current state of the given button."""
        if 0 <= button_number < len(self._buttons):
            return self._buttons[button_number]
        return 0

    def get_numhats(self):
        """Return the number of hat controls on the joystick."""
        return 1

    def get_hat(self, hat_number):
        """Get the current position of the hat control."""
        if hat_number == 0:
            return self._hat
        return (0, 0)

    def quit(self):
        """Uninitialize the joystick."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._initialized = False


def test_controller(controller_name):
    """Test the GameSirT1dPygame controller."""
    # Create and initialize the controller
    controller = GameSirT1dPygame(controller_name)
    print("Initializing controller...")
    if not controller.init():
        print("Failed to initialize controller.")
        return

    print(f"Controller: {controller.get_name()}")
    print(f"Axes: {controller.get_numaxes()}")
    print(f"Buttons: {controller.get_numbuttons()}")
    print(f"Hats: {controller.get_numhats()}")

    try:
        while True:
            # Read axes
            axes = [controller.get_axis(i) for i in range(controller.get_numaxes())]

            # Read buttons
            buttons = [
                controller.get_button(i) for i in range(controller.get_numbuttons())
            ]

            # Read hat
            hat = controller.get_hat(0)

            # Print state
            print(f"\rAxes: {axes}, Buttons: {buttons}, Hat: {hat}", end="")

            # Wait a bit
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        controller.quit()


if __name__ == "__main__":
    # Run the test if this file is executed directly
    test_controller("Gamesir-T1d-39BD")
