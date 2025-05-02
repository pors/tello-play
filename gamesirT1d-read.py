import asyncio
from bleak import BleakClient, BleakScanner

# The exact name our controller showed up as
CONTROLLER_NAME = "Gamesir-T1d-39BD"
# The characteristic we want to read
CHARACTERISTIC_UUID = "00008651-0000-1000-8000-00805f9b34fb"

class GameSirT1d:
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
        self.ly = ((data[3] & 0x3f) << 4) + (data[4] >> 4)
        self.rx = ((data[4] & 0xf) << 6) | (data[5] >> 2)
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
    
    # Add methods to get normalized values (-1.0 to 1.0) for joysticks
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

async def main():
    controller = GameSirT1d()
    
    print(f"Scanning for {CONTROLLER_NAME}...")
    device = await BleakScanner.find_device_by_name(CONTROLLER_NAME)
    
    if not device:
        print(f"Could not find {CONTROLLER_NAME}. Is it turned on?")
        return
    
    print(f"Found {CONTROLLER_NAME} at {device.address}")
    print("Connecting...")
    
    try:
        async with BleakClient(device.address) as client:
            print("Connected!")
            controller.connected = True
            controller._client = client
            
            try:
                while controller.connected:
                    # Read current state
                    data = await client.read_gatt_char(CHARACTERISTIC_UUID)
                    
                    # Parse the data
                    if controller.parse_data(data):
                        # Get normalized stick values for easier use
                        left_x, left_y = controller.get_left_stick()
                        right_x, right_y = controller.get_right_stick()
                        
                        # Clear the line and print current state
                        print(f"\rLeft: ({left_x:.2f}, {left_y:.2f}) Right: ({right_x:.2f}, {right_y:.2f}) | "
                              f"A:{controller.a} B:{controller.b} X:{controller.x} Y:{controller.y} "
                              f"L1:{controller.l1} R1:{controller.r1} L2:{controller.l2} R2:{controller.r2}", end="")
                    
                    # Wait a bit before next reading
                    await asyncio.sleep(0.05)  # 20Hz polling rate
                    
            except KeyboardInterrupt:
                print("\nStopping...")
                controller.connected = False
    
    except Exception as e:
        print(f"\nError: {e}")
        controller.connected = False

if __name__ == "__main__":
    print("GameSir T1d Controller Test")
    print("Move joysticks and press buttons to see values")
    print("Press Ctrl+C to exit")
    
    asyncio.run(main())