import machine
import network
import json
import urequests as requests
import time
import gc

# Load configuration from file
CONFIG_FILE = "door_config.json"

"""
Config file format:
{
    "device_name": "device_name",
    "wifi_name": "wifi_name",
    "wifi_password": "wifi_password",
    "server_url": "http://pat.local:5000",
    "gpio_pin": 16,
    "poll_interval": 0.5
}
"""

try:
    with open(CONFIG_FILE) as f:
        config = json.load(f)
except OSError:
    print(f"Configuration file '{CONFIG_FILE}' not found.")
    exit(1)

device_name = config.get("device_name", "default_door_sensor")
wifi_ssid = config.get("wifi_name", "your_wifi_ssid")
wifi_password = config.get("wifi_password", "your_wifi_password")
server_url = config.get("server_url", "http://pat.local:5000")
GPIO_PIN = config.get("gpio_pin", 16)
POLL_INTERVAL = config.get("poll_interval", 0.5)

print(
    f"Starting Door Sensor with Device ID: {device_name}, GPIO Pin: {GPIO_PIN}, Server URL: {server_url}"
)


# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)

    print(f"Connecting to Wi-Fi: {wifi_ssid}")
    for _ in range(10):
        if wlan.isconnected():
            break
        time.sleep(1)
        print("Connecting...")

    if wlan.isconnected():
        print("Connected to Wi-Fi:", wlan.ifconfig())
    else:
        print("Failed to connect to Wi-Fi. Restarting...")
        machine.reset()  # Restart the device if Wi-Fi fails


# Door Sensor Class
class DoorSensor:
    def __init__(self, pin, poll_interval, debug=False):
        self.pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.poll_interval = poll_interval
        self.current_state = self.pin.value()
        self.debug = debug
        print(f"Magnetic sensor initialized on GPIO pin {pin}.")

    def send_state(self, state):
        gc.collect()
        payload = {
            "device_name": device_name,
            "door_status": "CLOSED" if state == 0 else "OPEN",
            "battery": 100,  # Fake battery percentage
        }
        if self.debug:
            print(f"[DEBUG] Payload: {payload}")
        else:
            try:
                url = f"{server_url}/doors/add_data/door_status"
                headers = {"Content-Type": "application/json"}

                gc.collect()  # Free memory again before request
                response = requests.post(url, json=payload, headers=headers)

                print(f"Data sent with status code: {response.status_code}")

                response.close()
                gc.collect()
            except Exception as e:
                print(f"Failed to send data: {e}")

    def run(self):
        print("Starting sensor monitoring...")
        try:
            while True:
                state = self.pin.value()
                if state != self.current_state:
                    self.current_state = state
                    state_str = "CLOSED" if state == 0 else "OPEN"
                    print(f"Door is {state_str}.")
                    self.send_state(state)
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting...")
        finally:
            print("Program terminated.")


# Main execution
if __name__ == "__main__":
    connect_wifi()
    sensor = DoorSensor(pin=GPIO_PIN, poll_interval=POLL_INTERVAL, debug=False)
    sensor.run()
