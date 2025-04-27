# Tello Play

This repository contains basic scripts to control the Tello drone using Python. It uses the `djitellopy` library to communicate with the Tello drone.

## Table of Contents

- [Installation](#installation)
- [Setup](#setup)
- [How to Run the Scripts](#how-to-run-the-scripts)
- [License](#license)

## Installation

To get started, you need to install Python and the `djitellopy` library.

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/pors/tello-play.git
   cd tello-play
   ```

2. Install the required library `djitellopy` using pip:

   ```bash
   pip install djitellopy
   ```

3. Make sure your Python version is 3.7 or higher.

## Setup

Depending on if you use STA/router-mode or AP/direct mode, make sure the `host` field in `tello.Tello(host="192.168.1.85")` is set correctly or omitted.
For more information check [Dronelab - Router mode](tello.Tello(host="192.168.1.85")).

### Connecting to the Tello Drone
1. Turn on your Tello drone.
2. Connect your computer to the Tello drone's Wi-Fi network.
3. Once connected, you can use the scripts in this repository to control the drone.

Note that if you use STA/router-mode, the Tello and the computer need both the be connected to your router.

## How to Run the Scripts

To run any of the scripts, use the following command:

```bash
python <script_name>.py
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.


Feel free to customize this README further to suit your specific requirements. Let me know if you need additional sections or enhancements!
