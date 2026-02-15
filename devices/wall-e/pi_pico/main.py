import machine
import network
import json
import urequests as requests
import time
import gc
from machine import UART, Pin

# Load configuration from file
CONFIG_FILE = "wall-e_sampler_config.json"

"""
Config file format:
{
    "device_name": "device_name",
    "wifi_name": "wifi_name",
    "wifi_password": "wifi_password",
    "server_url": "http://pat.local:5000",
    "poll_interval": 300,
    "tx_pin": 4,
    "rx_pin": 5
}

Connections between SDS011 Sensor and Raspberry Pi Pico W:

SDS011 Sensor  | Raspberry Pi Pico W
-------------------------------------
TXD (Transmit) -> GPIO 5 (RX) (Pin 7)    (Configured as 'rx_pin')
RXD (Receive)  -> GPIO 4 (TX) (Pin 6)    (Configured as 'tx_pin')
GND (Ground)   -> GND (Pin 38 or any GND pin)
VCC (5V Power) -> VSYS (Pin 39)
"""

try:
    with open(CONFIG_FILE) as f:
        config = json.load(f)
except OSError:
    print(f"Configuration file '{CONFIG_FILE}' not found.")
    exit(1)

device_name = config.get("device_name", "default_air_sensor")
wifi_ssid = config.get("wifi_name", "your_wifi_ssid")
wifi_password = config.get("wifi_password", "your_wifi_password")
server_url = config.get("server_url", "http://pat.local:5000")
POLL_INTERVAL = config.get("poll_interval", 300)
TX_PIN = config.get("tx_pin", 4)
RX_PIN = config.get("rx_pin", 5)

print(
    f"Starting Air Quality Sensor with Device ID: {device_name}, Server URL: {server_url}"
)


# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)

    print(f"Connecting to Wi-Fi: {wifi_ssid}")
    for _ in range(10):  # Limit retries to avoid infinite loops
        if wlan.isconnected():
            break
        time.sleep(1)
        print("Connecting...")

    if wlan.isconnected():
        print("Connected to Wi-Fi:", wlan.ifconfig())
    else:
        print("Failed to connect to Wi-Fi. Restarting...")
        machine.reset()  # Restart the device if Wi-Fi fails


class AirQualitySensor:
    def __init__(self, poll_interval, tx_pin, rx_pin, debug=False):
        self.device_name = device_name
        self.server_url = server_url
        self.poll_interval = poll_interval
        self.debug = debug
        self.uart = UART(1, baudrate=9600, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.poll_count = 0
        self.reboot_interval = (
            144  # Reboot after 144 polls (12 hours with 300s interval)
        )
        print("Air Quality Sensor initialized.")

    def read_pm_sensor(self):
        """Read data from the PM sensor."""
        gc.collect()
        self.uart.write(b"\xaa\xc0")
        time.sleep(1)

        if self.uart.any():
            data = self.uart.read(10)
            if data and len(data) == 10 and data[0] == 0xAA and data[1] == 0xC0:
                pm25 = (data[2] + data[3] * 256) / 10.0
                pm10 = (data[4] + data[5] * 256) / 10.0
                return pm25, pm10
        return None, None

    def send_data(self, pm25, pm10):
        """Send air quality data to the server."""
        gc.collect()

        payload = {
            "device_name": self.device_name,
            "pm25": round(pm25, 1),
            "pm10": round(pm10, 1),
        }

        if self.debug:
            print(f"[DEBUG] Payload: {payload}")
        else:
            try:
                url = f"{self.server_url}/air/add_data"
                headers = {"Content-Type": "application/json"}

                gc.collect()
                response = requests.post(url, json=payload, headers=headers)

                print(f"Data sent with status code: {response.status_code}")

                response.close()
                gc.collect()
            except Exception as e:
                print(f"Failed to send data: {e}")

    def run(self):
        print("Starting air quality monitoring...")
        try:
            while True:
                pm25, pm10 = self.read_pm_sensor()
                if pm25 is not None and pm10 is not None:
                    print(f"PM2.5: {pm25}, PM10: {pm10}")
                    self.send_data(pm25, pm10)
                else:
                    print("Failed to read sensor data")

                self.poll_count += 1

                # Check if we need to reboot to refresh system resources
                if self.poll_count >= self.reboot_interval:
                    print(
                        f"Reboot interval ({self.reboot_interval} polls) reached. Rebooting..."
                    )
                    gc.collect()
                    time.sleep(2)  # Brief pause before reboot
                    machine.reset()

                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting...")
        finally:
            print("Program terminated.")


# Main execution
if __name__ == "__main__":
    connect_wifi()
    sensor = AirQualitySensor(
        poll_interval=POLL_INTERVAL, tx_pin=TX_PIN, rx_pin=RX_PIN, debug=False
    )
    sensor.run()
