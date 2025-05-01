import asyncio
from bleak import BleakClient, BleakScanner

# The name our controller should broadcast as
CONTROLLER_NAME = "Gamesir-T1d"


async def main():
    print("Starting BLE scan for GameSir-T1d controller...")

    # First, scan for all available BLE devices
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    # Print all found devices to help with debugging
    print(f"Found {len(devices)} Bluetooth devices:")
    for i, device in enumerate(devices):
        print(f"{i+1}. Name: {device.name}, Address: {device.address}")

    # Try to find our controller
    target_device = None
    for device in devices:
        if device.name and CONTROLLER_NAME.lower() in device.name.lower():
            target_device = device
            print(f"Found controller: {device.name}, Address: {device.address}")
            break

    if not target_device:
        print(f"No device found with name containing '{CONTROLLER_NAME}'")
        print("Is the controller turned on and in pairing mode?")
        return

    # Try to connect to the controller
    print(f"Attempting to connect to {target_device.name}...")
    try:
        async with BleakClient(target_device.address, timeout=10.0) as client:
            if client.is_connected:
                print(f"Successfully connected to {target_device.name}!")

                # List available services and characteristics
                print("\nAvailable services and characteristics:")
                for service in client.services:
                    print(f"Service: {service.uuid}")
                    for char in service.characteristics:
                        print(f"  Characteristic: {char.uuid}")
                        print(f"    Properties: {char.properties}")

                # Wait a moment so we can see the connection is established
                print("\nConnection successful. Press Ctrl+C to exit...")
                await asyncio.sleep(10)
            else:
                print("Failed to connect")
    except Exception as e:
        print(f"Error connecting to device: {e}")


if __name__ == "__main__":
    # Make sure controller is in pairing mode before running this
    print("Make sure the GameSir-T1d controller is turned on and in pairing mode.")
    print("(Typically hold power button until LEDs flash rapidly)")
    input("Press Enter to start scanning...")

    # Run the async main function
    asyncio.run(main())
