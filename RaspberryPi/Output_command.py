import socket
import json
from gpiozero import LED

# Map device names to GPIO pins
device_gpio_map = {
    "HEATING": LED(17),
    "WATERING": LED(27),
    "HUMIDIFIER": LED(22),
    "WATER_PUMP": LED(5),
    "LIGHTNING": LED(6)
}

HOST = ''
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server is running. Waiting for connections...")

    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            try:
                data = conn.recv(1024)
                if not data:
                    continue

                device_states = json.loads(data.decode('utf-8'))

                for device, state in device_states.items():
                    led = device_gpio_map.get(device.upper())
                    if led:
                        if state:
                            led.on()
                        else:
                            led.off()
                    else:
                        print(f"Unknown device: {device}")

            except (ConnectionResetError, json.JSONDecodeError) as e:
                print(f"Error with {addr}: {e}")
