import fetch from 'node-fetch';
import express from 'express';
import { WALL_EAccessory } from './wallEAccessory.js';
import { HodorAccessory } from './hodorAccessory.js';

export class CasaPAT {
  constructor(log, config, api) {
    log.info('Initializing CasaPat...');
    this.log = log;
    this.config = config;
    this.api = api;
    this.apiEndpoint = config.apiEndpoint;
    this.accessories = [];
    this.webhookServer = null;
    this.webhookPort = config.webhookPort || 8080;

    if (api) {
      this.api.on('didFinishLaunching', () => {
        this.log.debug('DidFinishLaunching');
        this.startWebhookServer();
        this.discoverDevices();
      });
    } else {
      this.log.error('API not available');
    }
  }

  startWebhookServer() {
    this.webhookServer = express();
    this.webhookServer.use(express.json());

    // Handle door webhook updates from the API
    // When a door sensor reports a state change, the API sends it here
    this.webhookServer.post('/webhook/doors', (req, res) => {
      const data = req.body;
      this.log.debug(`Received door webhook: ${JSON.stringify(data)}`);

      const accessory = this.accessories.find(acc => acc.context.device.DeviceName === data.device_name);
      if (accessory && accessory.context.type === 'doors') {
        const doorAccessory = accessory.doorAccessoryInstance;
        if (doorAccessory) {
          doorAccessory.updateFromWebhook(data);
        }
      }

      res.status(200).json({ status: 'received' });
    });

    // Handle air quality webhook updates
    this.webhookServer.post('/webhook/air', (req, res) => {
      const data = req.body;
      this.log.debug(`Received air webhook: ${JSON.stringify(data)}`);

      const accessory = this.accessories.find(acc => acc.context.device.DeviceName === data.device_name);
      if (accessory && accessory.context.type === 'air') {
        const airAccessory = accessory.airAccessoryInstance;
        if (airAccessory) {
          airAccessory.updateFromWebhook(data);
        }
      }

      res.status(200).json({ status: 'received' });
    });

    this.webhookServer.listen(this.webhookPort, () => {
      this.log.info(`Webhook server started on port ${this.webhookPort}`);
    });
  }

  async discoverDevices() {
    this.log.debug('Discovering devices...');

    const sensorTypes = [
      { type: 'air', endpoint: `${this.apiEndpoint}/air/get_devices/air_devices` },
      { type: 'doors', endpoint: `${this.apiEndpoint}/doors/get_devices/door_devices` }
    ];

    for (const sensor of sensorTypes) {
      try {
        this.log.debug(`Fetching ${sensor.type} devices from ${sensor.endpoint}`);
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
        this.log.debug(`Fetched device info for ${deviceName}: ${JSON.stringify(deviceInfo)}`);
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
      this.log.info(`Restoring existing ${type} accessory from cache: ${existingAccessory.displayName}`);
      this.createAccessoryHandler(type, existingAccessory, deviceInfo);
    } else {
      this.log.info(`Adding new ${type} accessory: ${deviceName}`);
      const accessory = new this.api.platformAccessory(deviceName, uuid);
      accessory.context.device = deviceInfo;
      accessory.context.type = type;
      this.createAccessoryHandler(type, accessory, deviceInfo);
      this.api.registerPlatformAccessories('homebridge-casapat', 'CasaPAT', [accessory]);
    }
  }

  createAccessoryHandler(type, accessory, deviceInfo) {
    if (type === 'air') {
      const airAccessory = new WALL_EAccessory(this.log, this.api, accessory, deviceInfo.DeviceName, this.apiEndpoint, deviceInfo);
      accessory.airAccessoryInstance = airAccessory;
    } else if (type === 'doors') {
      const doorAccessory = new HodorAccessory(this.log, this.api, accessory, deviceInfo.DeviceName, this.apiEndpoint, deviceInfo);
      accessory.doorAccessoryInstance = doorAccessory;
      this.registerDoorWebhook(deviceInfo.DeviceName);
    } else {
      this.log.error(`Unknown accessory type: ${type}`);
    }
  }

  async registerDoorWebhook(deviceName) {
    try {
      const webhookUrl = `http://localhost:${this.webhookPort}/webhook/doors`;
      this.log.debug(`Registering webhook for device: ${deviceName} at ${webhookUrl}`);

      const response = await fetch(`${this.apiEndpoint}/doors/webhook/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          webhook_url: webhookUrl,
          device_name: deviceName
        })
      });

      if (response.ok) {
        const result = await response.json();
        this.log.info(`Successfully registered webhook for device: ${deviceName}, webhook ID: ${result.webhook_id}`);
      } else {
        const errorText = await response.text();
        this.log.warn(`Failed to register webhook for device: ${deviceName}, status: ${response.status}, error: ${errorText}`);
      }
    } catch (error) {
      this.log.error(`Error registering webhook for device ${deviceName}: ${error}`);
    }
  }

  configureAccessory(accessory) {
    this.log.debug(`Configuring accessory: ${accessory.displayName}`);
    this.accessories.push(accessory);
  }
}