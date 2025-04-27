import socket
import time
import getpass
import os

# Environment variables for Wi-Fi credentials just to make it run in a notebook
os.environ["WIFI_SSID"] = "MyNetwork"
os.environ["WIFI_PASSWORD"] = "SuperSecret"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)


def get_wifi_credentials():
    try:
        ssid = input("Wi-Fi SSID: ")
        password = getpass.getpass("Wi-Fi Password: ")
    except (EOFError, getpass.GetPassWarning, Exception):
        # Fall back to environment variables
        print("Interactive input not available. Falling back to environment variables.")
        ssid = os.getenv("WIFI_SSID")
        password = os.getenv("WIFI_PASSWORD")

        if not ssid or not password:
            raise RuntimeError(
                "Missing WIFI_SSID or WIFI_PASSWORD environment variable."
            )

    return ssid, password


# Step 1: Enter SDK mode
sock.sendto(b"command", ("192.168.10.1", 8889))
try:
    response, _ = sock.recvfrom(1024)
    print("Response 1:", response)
except Exception as e:
    print("No response to command:", e)

time.sleep(1)

# Step 2: Send ap command
ssid, password = get_wifi_credentials()
sock.sendto(b"ap %s %s" % (ssid.encode(), password.encode()), ("192.168.10.1", 8889))
try:
    response, _ = sock.recvfrom(1024)
    print("Response 2:", response)
except Exception as e:
    print("No response to ap:", e)
