import RPi.GPIO as GPIO
import time
import logging
import os
import json
import requests
import argparse
from datetime import datetime, timezone

# Configure logging
LOG_DIR = "/var/log/door"
LOG_FILE_DOOR = os.path.join(LOG_DIR, "door_sensor.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE_DOOR), logging.StreamHandler()],
)


# Load configuration
CONFIG_FILE = "door_config.json"
if not os.path.exists(CONFIG_FILE):
    logging.error(f"Configuration file '{CONFIG_FILE}' not found.")
    exit(1)

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

device_id = config.get("device_id", "default_door_sensor")
server_url = config.get("server_url", "http://pat.local:5000")
GPIO_PIN = config.get("gpio_pin", 11)
POLL_INTERVAL = config.get("poll_interval", 0.5)

logging.info(
    f"Starting Door Sensor with Device ID: {device_id}, GPIO Pin: {GPIO_PIN}, Server URL: {server_url}"
)


class DoorSensor:
    def __init__(self, pin, poll_interval, debug=False):
        self.pin = pin
        self.poll_interval = poll_interval
        self.current_state = None
        self.debug = debug

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        logging.info(f"Magnetic sensor initialized on GPIO pin {self.pin}.")

    def send_state(self, state):
        payload = {
            "device_id": device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "door_status": "CLOSED" if state == GPIO.LOW else "OPEN",
            "battery": 100,
        }
        if self.debug:
            logging.info(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")
        else:
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.post(
                    f"{server_url}/doors/add_data/door_status",
                    headers=headers,
                    data=json.dumps(payload),
                )
                logging.info(
                    f"Data sent with status code: {response.status_code}, response body: {response.text}"
                )
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to send data: {e}")

    def run(self):
        try:
            logging.info("Starting sensor monitoring...")
            while True:
                state = GPIO.input(self.pin)
                if state != self.current_state:
                    self.current_state = state
                    state_str = "CLOSED" if state == GPIO.LOW else "OPEN"
                    logging.info(f"Door is {state_str}.")
                    self.send_state(state)
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt detected. Exiting...")
        finally:
            GPIO.cleanup()
            logging.info("GPIO cleanup complete. Program terminated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Door Sensor Logger")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to print payload instead of sending data",
    )
    args = parser.parse_args()

    sensor = DoorSensor(pin=GPIO_PIN, poll_interval=POLL_INTERVAL, debug=args.debug)
    sensor.run()
