import requests
import time

def read_sensor():
    RPI_IP = '192.168.16.54'  # Replace with your Pi’s IP

    try:
        response = requests.get(f'http://{RPI_IP}:5000/sensor')
        response.raise_for_status()
        data = response.json()

        temperature = data['temperature']
        soil_moisture = data['soil_moisture']
        humidity = data['humidity']

        return temperature, soil_moisture, humidity

    except requests.RequestException as e:
        print("Failed to get sensor data:", e)
        return None, None, None

# # Example usage
# while True:
#     temp, moisture, hum = read_sensor()
#     if temp is not None:
#         print(f"Temperature: {temp}, Soil Moisture: {moisture}, Humidity: {hum}")
#     time.sleep(2)
