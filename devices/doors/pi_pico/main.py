import machine
import network
import json
import urequests as requests
import time
import gc
import sys

# Load configuration from file
CONFIG_FILE = "door_config.json"

# Watchdog configuration
WATCHDOG_TIMEOUT = 8  # Reset if no activity for 8 seconds (max allowed is ~8.4s)
MEMORY_CHECK_INTERVAL = 30  # Check memory every 30 seconds
MIN_FREE_MEMORY = 50000  # Reboot if free memory below 50KB
RESTART_INTERVAL = 43200  # Restart device every 12 hours (in seconds)
REQUEST_TIMEOUT = 10  # HTTP request timeout in seconds
CONSECUTIVE_FAILURES_LIMIT = 10  # Reboot after 10 consecutive failures

# Initialize watchdog
wdt = machine.WDT(timeout=WATCHDOG_TIMEOUT * 1000)  # Convert to milliseconds

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

# Runtime tracking
start_time = time.time()
last_memory_check = 0
consecutive_failures = 0

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
        self.consecutive_failures = 0
        print(f"Magnetic sensor initialized on GPIO pin {pin}.")

    def send_state(self, state):
        global consecutive_failures
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
                # Send request with timeout
                response = requests.post(
                    url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT
                )

                print(f"Data sent with status code: {response.status_code}")
                response.close()
                gc.collect()

                # Reset failure counter on success
                consecutive_failures = 0

            except Exception as e:
                print(f"Failed to send data: {e}")
                consecutive_failures += 1
                if consecutive_failures >= CONSECUTIVE_FAILURES_LIMIT:
                    print(
                        f"Consecutive failures limit ({CONSECUTIVE_FAILURES_LIMIT}) reached. Rebooting..."
                    )
                    machine.reset()

    def check_memory_and_uptime(self):
        """Check memory usage and uptime, reboot if needed"""
        global last_memory_check, start_time

        current_time = time.time()

        # Check memory every MEMORY_CHECK_INTERVAL seconds
        if current_time - last_memory_check > MEMORY_CHECK_INTERVAL:
            last_memory_check = current_time
            gc.collect()
            free_mem = gc.mem_free()

            print(f"Memory status: {free_mem} bytes free")

            if free_mem < MIN_FREE_MEMORY:
                print(f"Critical memory low: {free_mem} bytes. Rebooting...")
                machine.reset()

        # Check if device has been running too long
        uptime = current_time - start_time
        if uptime > RESTART_INTERVAL:
            print(
                f"Uptime {uptime}s exceeded {RESTART_INTERVAL}s. Performing scheduled restart..."
            )
            machine.reset()

    def run(self):
        print("Starting sensor monitoring...")
        try:
            while True:
                # Feed watchdog to prevent timeout
                wdt.feed()

                # Check health status
                self.check_memory_and_uptime()

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
