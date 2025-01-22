#!/usr/bin/env python3

import serial
import time
import requests
import json
import logging
import os
import argparse

# Configure logging for the sampler
LOG_DIR = "/var/log/wall-e"
LOG_FILE_SAMPLER = os.path.join(LOG_DIR, "wall-e_sampler.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE_SAMPLER), logging.StreamHandler()],
)

# Load configuration
CONFIG_FILE = "wall-e_sampler_config.json"
if not os.path.exists(CONFIG_FILE):
    logging.error(f"Configuration file '{CONFIG_FILE}' not found.")
    exit(1)

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

device_name = config.get("device_name", "default_device")
server_url = config.get("server_url", "http://pat.local:5000")

logging.info(
    f"Starting WALL-E Sampler with Device ID: {device_name}, Server URL: {server_url}"
)


# Sampler functions
def read_pm_sensor(port):
    """Read data from the PM sensor."""
    ser = serial.Serial(port, baudrate=9600, timeout=2)
    try:
        data = ser.read(10)
        if data[0] == 0xAA and data[1] == 0xC0:
            pm25 = (data[2] + data[3] * 256) / 10.0
            pm10 = (data[4] + data[5] * 256) / 10.0
            return pm25, pm10
    finally:
        ser.close()
    return None, None


def send_data(device_name, pm25, pm10, debug):
    """Send air quality data to the server or print in debug mode."""
    payload = {
        "device_name": device_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pm25": pm25,
        "pm10": pm10,
    }
    if debug:
        logging.info(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")
        return 200
    else:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            server_url + "/air/add_data", headers=headers, data=json.dumps(payload)
        )
        return response.status_code, response.content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WALL-E Air Sampler")
    parser.add_argument(
        "--pins", action="store_true", help="Use GPIO pins instead of USB"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to print payload instead of sending data",
    )
    args = parser.parse_args()

    # Select the appropriate port
    port = "/dev/serial0" if args.pins else "/dev/ttyUSB0"
    logging.info(f"Using port: {port}")

    while True:
        try:
            pm25, pm10 = read_pm_sensor(port)
            logging.info(f"Readings - PM2.5: {pm25}, PM10: {pm10}")
            if pm25 is not None and pm10 is not None:
                status_code, message = send_data(device_name, pm25, pm10, args.debug)
                logging.info(
                    f"Data {'printed (debug mode)' if args.debug else 'sent'} with status code: {status_code} and message: {message}"
                )
        except requests.exceptions.ConnectionError:
            logging.error("Failed to connect to the server. The server might be down.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        time.sleep(300)
