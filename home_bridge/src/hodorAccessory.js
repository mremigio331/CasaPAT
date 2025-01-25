import fetch from 'node-fetch';

export class HodorAccessory {
  constructor(log, api, accessory, device, apiEndpoint, deviceInfo) {
    this.log = log;
    this.api = api;
    this.accessory = accessory;
    this.device = device;
    this.apiEndpoint = apiEndpoint;
    this.deviceInfo = deviceInfo;

    this.log.info(`Initializing accessory for door sensor: ${device}`);

    this.accessory.getService(this.api.hap.Service.AccessoryInformation)
      .setCharacteristic(this.api.hap.Characteristic.Manufacturer, this.deviceInfo.DeviceManufacturer)
      .setCharacteristic(this.api.hap.Characteristic.Model, this.deviceInfo.DeviceModel)
      .setCharacteristic(this.api.hap.Characteristic.SerialNumber, this.device);

    this.doorSensorService = this.accessory.getService(this.api.hap.Service.ContactSensor) ||
                             this.accessory.addService(this.api.hap.Service.ContactSensor, 'Hodor Door Sensor');

    this.doorSensorService.getCharacteristic(this.api.hap.Characteristic.ContactSensorState)
      .on('get', this.getDoorState.bind(this));

    this.batteryService = this.accessory.getService(this.api.hap.Service.BatteryService) ||
                          this.accessory.addService(this.api.hap.Service.BatteryService, 'Hodor Battery');

    this.batteryService.getCharacteristic(this.api.hap.Characteristic.BatteryLevel)
      .on('get', this.getBatteryLevel.bind(this));

    // Set up periodic polling
    this.pollingInterval = setInterval(this.pollData.bind(this), 300000); // Poll every 5 minutes
  }

  async fetchData() {
    this.log.info(`Fetching data for door sensor: ${this.device}`);
    try {
      const response = await fetch(`${this.apiEndpoint}/doors/info/latest?device=${this.device}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      this.log.info(`Fetched data for door sensor ${this.device}: ${JSON.stringify(data)}`);
      return data.latest_info;
    } catch (error) {
      this.log.error(`Error fetching data for ${this.device}: ${error}`);
      return null;
    }
  }

  async getDoorState(callback) {
    const data = await this.fetchData();
    if (!data) {
      this.log.warn(`No data received for door sensor: ${this.device}`);
      callback(null, this.api.hap.Characteristic.ContactSensorState.CONTACT_NOT_DETECTED);
      return;
    }

    try {
      const doorState = this.parseDoorState(data.current_state);
      callback(null, doorState);
    } catch (error) {
      this.log.error(`Error getting door state: ${error}`);
      callback(error);
    }
  }

  async getBatteryLevel(callback) {
    const data = await this.fetchData();
    if (!data) {
      this.log.warn(`No data received for battery level: ${this.device}`);
      callback(null, 0);
      return;
    }

    try {
      const batteryLevel = parseInt(data.battery, 10);
      callback(null, batteryLevel);
    } catch (error) {
      this.log.error(`Error getting battery level: ${error}`);
      callback(error);
    }
  }

  async pollData() {
    this.log.info(`Polling data for door sensor: ${this.device}`);
    const data = await this.fetchData();
    if (data) {
      try {
        const doorState = this.parseDoorState(data.current_state);
        const batteryLevel = parseInt(data.battery, 10);

        this.doorSensorService.updateCharacteristic(this.api.hap.Characteristic.ContactSensorState, doorState);
        this.batteryService.updateCharacteristic(this.api.hap.Characteristic.BatteryLevel, batteryLevel);

        // Add logging to confirm updates
        this.log.info(`Updated door state for ${this.device}: ${data.current_state}`);
        this.log.info(`Updated battery level for ${this.device}: ${data.battery}%`);
      } catch (error) {
        this.log.error(`Error updating door sensor data: ${error}`);
      }
    }
  }

  parseDoorState(state) {
    this.log.info(`Parsing door state for ${this.device}: ${state}`);

    if (state === 'CLOSED') {
      this.log.info(`Door sensor ${this.device} is CLOSED`);
      return this.api.hap.Characteristic.ContactSensorState.CONTACT_DETECTED;
    } else if (state === 'OPEN') {
      this.log.info(`Door sensor ${this.device} is OPEN`);
      return this.api.hap.Characteristic.ContactSensorState.CONTACT_NOT_DETECTED;
    } else {
      this.log.warn(`Unknown door state for device ${this.device}: ${state}`);
      return this.api.hap.Characteristic.ContactSensorState.CONTACT_NOT_DETECTED;
    }
  }
}
