# Dronelab.dev: Tello Play

This repository contains basic scripts to control the Tello drone using Python. It uses the `djitellopy` library to communicate with the Tello drone.

These scripts accompany the blog posts on [dronelab.dev](https://dronelab.dev).

## Table of Contents

- [Installation](#installation)
- [Setup](#setup)
- [How to Run the Scripts](#how-to-run-the-scripts)
- [Scripts Overview](#scripts-overview)
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
For more information check [Dronelab - Router mode](https://dronelab.dev/posts/crash-the-tello/#using-router-mode).

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

## Scripts Overview

Here's a list of all the Python scripts in this repository and what each one does:

- **connected_test.py**: A simple script to check if the Tello drone is connected, displaying battery level and temperature.

- **fly.py**: Basic flight example that connects to the Tello, takes off, performs several simple movements using RC controls, and then lands.

- **gamesirT1d-connect.py**: Script to discover and connect to a GameSir T1d Bluetooth controller, displaying available services and characteristics.

- **gamesirT1d-read.py**: Reads and displays real-time input data from a GameSir T1d controller including joystick positions and button states.

- **gamesir_t1d_pygame.py**: Core implementation of a pygame-compatible interface for the GameSir T1d controller, providing a consistent interface that works with pygame.

- **gamesir_t1d_pygame_example.py**: Example showing how to use the pygame wrapper for the GameSir T1d controller, visualizing joystick movements.

- **image-capture.py**: Streams video from the Tello's camera, displays it in a window, and allows for quitting with the 'q' key.

- **manual-control-pygame.py**: Full-featured script for controlling the Tello drone with keyboard inputs using pygame, displaying video feed with battery status.

- **set-wifi.py**: Utility to configure the Tello to connect to a WiFi network (router mode), accepting SSID and password input.

- **tello_controller_sim.py**: A simulator for testing Tello drone controls without using a physical drone, visualizing drone position and movement.

- **tello_gamesir_controller.py**: Demo script that visualizes the inputs from a GameSir T1d controller without connecting to a drone.

The repository also includes a `tello_images` directory where screenshots captured from the drone camera are stored.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
