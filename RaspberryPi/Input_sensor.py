import smbus
import time
from flask import Flask, jsonify

app = Flask(__name__)
bus = smbus.SMBus(1)
address = 0x48

def read_sensor(channel):
    if channel < 0 or channel > 3:
        raise ValueError("Channel must be 0-3")
    
    control_byte = 0x40 | channel  # Select AINx
    bus.write_byte(address, control_byte)
    bus.read_byte(address)  # Dummy read
    analog_value = bus.read_byte(address)
    return analog_value

@app.route('/sensor')
def sensor_data():
    temperature = read_sensor(0)      # AIN0
    soil_moisture = read_sensor(1)    # AIN1
    humidity = read_sensor(2)         # AIN2
    return jsonify({
        "temperature": temperature,
        "soil_moisture": soil_moisture,
        "humidity": humidity
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
