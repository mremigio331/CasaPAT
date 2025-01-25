import fetch from 'node-fetch';

export class WALL_EAccessory {
  constructor(log, api, accessory, device, apiEndpoint, deviceInfo) {
    this.log = log;
    this.api = api;
    this.accessory = accessory;
    this.device = device;
    this.apiEndpoint = apiEndpoint;
    this.deviceInfo = deviceInfo;

    this.log.info(`Initializing accessory for device: ${device}`);

    this.accessory.getService(this.api.hap.Service.AccessoryInformation)
      .setCharacteristic(this.api.hap.Characteristic.Manufacturer, this.deviceInfo.DeviceManufacturer)
      .setCharacteristic(this.api.hap.Characteristic.Model, this.deviceInfo.DeviceModel)
      .setCharacteristic(this.api.hap.Characteristic.SerialNumber, device);

    this.airQualityService = this.accessory.getService(this.api.hap.Service.AirQualitySensor) ||
                              this.accessory.addService(this.api.hap.Service.AirQualitySensor, 'WALL-E Sensor');

    this.airQualityService.getCharacteristic(this.api.hap.Characteristic.AirQuality)
      .on('get', this.getAirQuality.bind(this));

    this.pm10Characteristic = this.airQualityService.getCharacteristic(this.api.hap.Characteristic.PM10Density) ||
                              this.airQualityService.addCharacteristic(this.api.hap.Characteristic.PM10Density);

    this.pm25Characteristic = this.airQualityService.getCharacteristic(this.api.hap.Characteristic.PM2_5Density) ||
                              this.airQualityService.addCharacteristic(this.api.hap.Characteristic.PM2_5Density);

    // Set up periodic polling
    this.pollingInterval = setInterval(this.pollData.bind(this), 300000); // Poll every 5 minutes
  }

  async fetchData() {
    this.log.info(`Fetching data for device: ${this.device}`);
    try {
      const response = await fetch(`${this.apiEndpoint}/air/info/latest?device=${this.device}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      this.log.info(`Fetched data for device ${this.device}: ${JSON.stringify(data)}`);
      return data.data;
    } catch (error) {
      this.log.error(`Error fetching data for ${this.device}: ${error}`);
      return null;
    }
  }

  async getAirQuality(callback) {
    const data = await this.fetchData();
    if (!data) {
      this.log.warn(`No data received for device: ${this.device}`);
      callback(null, this.api.hap.Characteristic.AirQuality.UNKNOWN);
      return;
    }

    try {
      const airQuality = this.parseAirQuality(data);
      this.pm10Characteristic.updateValue(parseFloat(data.PM10));
      this.pm25Characteristic.updateValue(parseFloat(data.PM25));
      callback(null, airQuality);
    } catch (error) {
      this.log.error(`Error getting air quality: ${error}`);
      callback(error);
    }
  }

  async pollData() {
    this.log.info(`Polling data for device: ${this.device}`);
    const data = await this.fetchData();
    if (data) {
      try {
        const airQuality = this.parseAirQuality(data);
        this.pm10Characteristic.updateValue(parseFloat(data.PM10));
        this.pm25Characteristic.updateValue(parseFloat(data.PM25));
        this.airQualityService.updateCharacteristic(this.api.hap.Characteristic.AirQuality, airQuality);

        // Add logging to confirm updates
        this.log.info(`Updated PM10 for device ${this.device}: ${data.PM10}`);
        this.log.info(`Updated PM25 for device ${this.device}: ${data.PM25}`);
        this.log.info(`Updated Air Quality for device ${this.device}: ${airQuality}`);
      } catch (error) {
        this.log.error(`Error updating air quality: ${error}`);
      }
    }
  }

  parseAirQuality(data) {
    const code = data.code;
    this.log.info(`Parsing air quality code ${code} for device ${this.device}`);

    switch (code) {
      case "1":
        this.log.info(`Air quality for device ${this.device} is EXCELLENT`);
        return this.api.hap.Characteristic.AirQuality.EXCELLENT;
      case "2":
        this.log.info(`Air quality for device ${this.device} is GOOD`);
        return this.api.hap.Characteristic.AirQuality.GOOD;
      case "3":
        this.log.info(`Air quality for device ${this.device} is FAIR`);
        return this.api.hap.Characteristic.AirQuality.FAIR;
      case "4":
        this.log.info(`Air quality for device ${this.device} is INFERIOR`);
        return this.api.hap.Characteristic.AirQuality.INFERIOR;
      case "5":
        this.log.info(`Air quality for device ${this.device} is POOR`);
        return this.api.hap.Characteristic.AirQuality.POOR;
      default:
        this.log.warn(`Unknown air quality code for device ${this.device}: ${code}`);
        return this.api.hap.Characteristic.AirQuality.UNKNOWN;
    }
  }
}
