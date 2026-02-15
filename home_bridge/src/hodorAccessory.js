import fetch from 'node-fetch';

export class HodorAccessory {
  constructor(log, api, accessory, device, apiEndpoint, deviceInfo) {
    this.log = log;
    this.api = api;
    this.accessory = accessory;
    this.device = device;
    this.apiEndpoint = apiEndpoint;
    this.deviceInfo = deviceInfo;
    
    // Cache for current state - receives updates via webhooks
    this.cachedDoorState = null;
    this.cachedBatteryLevel = null;

    this.log.info(`Initializing accessory for door sensor: ${device}`);

    this.accessory.getService(this.api.hap.Service.AccessoryInformation)
      .setCharacteristic(this.api.hap.Characteristic.Manufacturer, this.deviceInfo.DeviceManufacturer)
      .setCharacteristic(this.api.hap.Characteristic.Model, this.deviceInfo.DeviceModel)
      .setCharacteristic(this.api.hap.Characteristic.SerialNumber, this.device);

    this.doorSensorService = this.accessory.getService(this.api.hap.Service.ContactSensor) ||
                             this.accessory.addService(this.api.hap.Service.ContactSensor, 'Hodor Door Sensor');

    this.batteryService = this.accessory.getService(this.api.hap.Service.BatteryService) ||
                          this.accessory.addService(this.api.hap.Service.BatteryService, 'Hodor Battery');

    // Fetch initial state on startup to populate HomeKit immediately
    // Subsequent updates will be delivered via webhooks
    this.fetchInitialState();
  }

  async fetchData() {
    const url = `${this.apiEndpoint}/doors/info/latest?device_name=${this.device}`;
    this.log.debug(`Fetching data for door sensor: ${this.device} from ${url}`);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 4000); // 4s timeout
    try {
      const response = await fetch(url, { signal: controller.signal });
      if (!response.ok) {
        this.log.error(`HTTP error for ${this.device}: status=${response.status} url=${url}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const latestInfo = data.latest_info;
      
      if (latestInfo) {
        // Initialize cache with current state
        // Future updates will come via webhooks instead of polling
        this.updateFromWebhook({
          door_status: latestInfo.door_status,
          battery: latestInfo.battery,
          device_name: this.device,
          timestamp: latestInfo.timestamp
        });
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        this.log.error(`Timeout fetching data for ${this.device}: request exceeded 4s (url=${url})`);
      } else {
        this.log.error(`Error fetching data for ${this.device}: ${error.message} (type=${error.type ?? error.name}, url=${url})`);
      }
      return null;
    } finally {
      clearTimeout(timeout);
    }
  }

  async getDoorState(callback) {
    const data = await this.fetchData();
    this.log.debug(`Door: ${this.device}, Data: ${JSON.stringify(data)}`);
    if (!data) {
      this.log.warn(`No data received for door sensor: ${this.device}`);
      callback(null, this.api.hap.Characteristic.ContactSensorState.CONTACT_NOT_DETECTED);
      return;
    }

    try {
      const doorState = this.parseDoorState(data.door_status);
      const batteryLevel = parseInt(data.battery, 10);

      // Update cache with new state
      this.cachedDoorState = doorState;
      this.cachedBatteryLevel = batteryLevel;

      // Push updates to HomeKit - this will notify Home app of status changes
      this.doorSensorService.updateCharacteristic(this.api.hap.Characteristic.ContactSensorState, doorState);
      this.batteryService.updateCharacteristic(this.api.hap.Characteristic.BatteryLevel, batteryLevel);

      this.log.info(`Updated door state for ${this.device}: ${data.door_status}, Battery: ${batteryLevel}%`);
    } catch (error) {
      this.log.error(`Error updating from webhook: ${error}`);
    }
  }
  parseDoorState(state) {
    this.log.debug(`Parsing door state for ${this.device}: ${state}`);

    if (state === 'CLOSED') {
      this.log.debug(`Door sensor ${this.device} is CLOSED`);
      return this.api.hap.Characteristic.ContactSensorState.CONTACT_DETECTED;
    } else if (state === 'OPEN') {
      this.log.debug(`Door sensor ${this.device} is OPEN`);
      return this.api.hap.Characteristic.ContactSensorState.CONTACT_NOT_DETECTED;
    } else {
      this.log.warn(`Unknown door state for device ${this.device}: ${state}`);
      return this.api.hap.Characteristic.ContactSensorState.CONTACT_NOT_DETECTED;
    }
  }
}