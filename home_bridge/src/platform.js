import fetch from 'node-fetch';
import { WALL_EAccessory } from './wallEAccessory.js';
import { HodorAccessory } from './hodorAccessory.js';


export class CasaPAT {
  constructor(log, config, api) {
    log('Initializing CasaPat...');
    this.log = log;
    this.config = config;
    this.api = api;
    this.apiEndpoint = config.apiEndpoint;
    this.accessories = [];

    if (api) {
      this.api.on('didFinishLaunching', () => {
        this.log('DidFinishLaunching');
        this.discoverDevices();
      });
    } else {
      this.log.error('API not available');
    }
  }

  async discoverDevices() {
    this.log('Discovering devices...');

    const sensorTypes = [
      { type: 'air', endpoint: `${this.apiEndpoint}/air/get_devices/air_devices` },
      { type: 'doors', endpoint: `${this.apiEndpoint}/doors/get_devices/door_devices` }
    ];

    for (const sensor of sensorTypes) {
      try {
        this.log(`Fetching ${sensor.type} devices from ${sensor.endpoint}`);
        const response = await fetch(sensor.endpoint);
        const devicesData = await response.json();

        if (devicesData && devicesData.devices) {
          for (const device of devicesData.devices) {
            await this.fetchDeviceInfoAndAdd(device, sensor.type);
          }
        } else {
          this.log.error(`Invalid response format for ${sensor.type} devices: ${JSON.stringify(devicesData)}`);
        }
      } catch (error) {
        this.log.error(`Error discovering ${sensor.type} devices: ${error}`);
      }
    }
  }

  async fetchDeviceInfoAndAdd(device, type) {
    try {
      const infoResponse = await fetch(`${this.apiEndpoint}/${type}/info/device?device_name=${device}`);
      if (!infoResponse.ok) {
        throw new Error(`HTTP error! status: ${infoResponse.status}`);
      }

      const deviceInfo = await infoResponse.json();
      const deviceID = deviceInfo.device_info.DeviceID;
      const deviceName = deviceInfo.device_info.DeviceName;

      if (deviceID && deviceName) {
        this.log(`Fetched device info for ${deviceName}: ${JSON.stringify(deviceInfo)}`);
        this.addAccessory(deviceID, deviceName, type, deviceInfo.device_info);
      } else {
        this.log.error(`Invalid device info format for ${device}: ${JSON.stringify(deviceInfo)}`);
      }
    } catch (error) {
      this.log.error(`Error fetching device info for ${device}: ${error}`);
    }
  }

  addAccessory(deviceID, deviceName, type, deviceInfo) {
    const uuid = this.api.hap.uuid.generate(deviceName);
    const existingAccessory = this.accessories.find(accessory => accessory.UUID === uuid);

    if (existingAccessory) {
      this.log(`Restoring existing ${type} accessory from cache: ${existingAccessory.displayName}`);
      this.createAccessoryHandler(type, existingAccessory, deviceInfo);
    } else {
      this.log(`Adding new ${type} accessory: ${deviceName}`);
      const accessory = new this.api.platformAccessory(deviceName, uuid);
      accessory.context.device = deviceInfo;
      accessory.context.type = type;
      this.createAccessoryHandler(type, accessory, deviceInfo);
      this.api.registerPlatformAccessories('homebridge-casapat', 'CasaPAT', [accessory]);
    }
  }

  createAccessoryHandler(type, accessory, deviceInfo) {
    if (type === 'air') {
      new WALL_EAccessory(this.log, this.api, accessory, deviceInfo.DeviceName, this.apiEndpoint, deviceInfo);
    } else if (type === 'doors') {
      new HodorAccessory(this.log, this.api, accessory, deviceInfo.DeviceName, this.apiEndpoint, deviceInfo);
    } else {
      this.log.error(`Unknown accessory type: ${type}`);
    }
  }

  configureAccessory(accessory) {
    this.log(`Configuring accessory: ${accessory.displayName}`);
    this.accessories.push(accessory);
  }
}