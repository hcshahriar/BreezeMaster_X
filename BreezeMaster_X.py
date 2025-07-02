import time
import random
import threading
from flask import Flask, request, jsonify

class AirCooler:
    def __init__(self):
        self.power = False
        self.temperature = 30
        self.humidity = 50
        self.fan_speed = 0
        self.water_level = 100
        self.ideal_temp = 25
        self.ideal_humidity = 60
        self.timer = None
        self.timer_duration = 0
        self.timer_running = False

    def toggle_power(self):
        self.power = not self.power
        if not self.power:
            self.fan_speed = 0
            self.cancel_timer()
        return f"Power {'ON' if self.power else 'OFF'}"

    def set_temperature(self, temp):
        self.ideal_temp = temp
        return f"Target temperature set to {temp}°C"

    def set_humidity(self, humidity):
        self.ideal_humidity = humidity
        return f"Target humidity set to {humidity}%"

    def set_fan_speed(self, speed):
        if not self.power:
            return "Cannot set fan speed - power is OFF"
        self.fan_speed = max(0, min(3, speed))
        return f"Fan speed set to {self.fan_speed}"

    def refill_water(self):
        self.water_level = 100
        return "Water tank refilled"

    def set_timer(self, minutes):
        self.cancel_timer()
        if minutes <= 0:
            return "Timer cancelled"
        
        self.timer_duration = minutes * 60
        self.timer_running = True
        self.timer = threading.Timer(self.timer_duration, self.timer_callback)
        self.timer.start()
        return f"Timer set for {minutes} minutes"

    def cancel_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer_running = False
        return "Timer cancelled"

    def timer_callback(self):
        self.toggle_power()
        self.timer_running = False

    def update_sensors(self):
        self.temperature += random.uniform(-1, 1)
        self.humidity += random.uniform(-2, 2)
        if self.power and self.fan_speed > 0:
            self.water_level -= 0.1
        self.temperature = max(15, min(40, self.temperature))
        self.humidity = max(30, min(90, self.humidity))
        self.water_level = max(0, min(100, self.water_level))

    def auto_adjust(self):
        if not self.power:
            return None
        
        temp_diff = self.temperature - self.ideal_temp
        humidity_diff = self.humidity - self.ideal_humidity
        
        if self.water_level < 20:
            self.fan_speed = 0
            return "Water level low - please refill"
        
        if temp_diff > 5 or humidity_diff > 10:
            self.fan_speed = 3
        elif temp_diff > 2 or humidity_diff > 5:
            self.fan_speed = 2
        elif temp_diff > 0 or humidity_diff > 0:
            self.fan_speed = 1
        else:
            self.fan_speed = 0

    def get_status(self):
        return {
            "power": self.power,
            "current_temperature": round(self.temperature, 1),
            "current_humidity": round(self.humidity, 1),
            "fan_speed": self.fan_speed,
            "water_level": round(self.water_level, 1),
            "target_temperature": self.ideal_temp,
            "target_humidity": self.ideal_humidity,
            "timer_running": self.timer_running,
            "timer_remaining": max(0, self.timer_duration - (time.time() - self.timer_start_time)) if self.timer_running else 0
        }

app = Flask(__name__)
cooler = AirCooler()

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(cooler.get_status())

@app.route('/api/power', methods=['POST'])
def power_control():
    result = cooler.toggle_power()
    return jsonify({"message": result})

@app.route('/api/temperature', methods=['POST'])
def set_temperature():
    data = request.get_json()
    result = cooler.set_temperature(data['temperature'])
    return jsonify({"message": result})

@app.route('/api/humidity', methods=['POST'])
def set_humidity():
    data = request.get_json()
    result = cooler.set_humidity(data['humidity'])
    return jsonify({"message": result})

@app.route('/api/fan', methods=['POST'])
def set_fan():
    data = request.get_json()
    result = cooler.set_fan_speed(data['speed'])
    return jsonify({"message": result})

@app.route('/api/refill', methods=['POST'])
def refill():
    result = cooler.refill_water()
    return jsonify({"message": result})

@app.route('/api/timer', methods=['POST'])
def set_timer():
    data = request.get_json()
    result = cooler.set_timer(data['minutes'])
    return jsonify({"message": result})

def sensor_loop():
    while True:
        cooler.update_sensors()
        cooler.auto_adjust()
        time.sleep(2)

if __name__ == "__main__":
    sensor_thread = threading.Thread(target=sensor_loop)
    sensor_thread.daemon = True
    sensor_thread.start()
    
    app.run(host='0.0.0.0', port=5000)
