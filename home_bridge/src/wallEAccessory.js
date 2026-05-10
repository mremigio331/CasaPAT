import fetch from 'node-fetch';

export class WALL_EAccessory {
  constructor(log, api, accessory, device, apiEndpoint, deviceInfo) {
    this.log = log;
    this.api = api;
    this.accessory = accessory;
    this.device = device;
    this.apiEndpoint = apiEndpoint;
    this.deviceInfo = deviceInfo;

    this.cachedAirQuality = null;
    this.cachedPM10 = null;
    this.cachedPM25 = null;

    this.log.info(`Initializing accessory for device: ${device}`);

    this.accessory.getService(this.api.hap.Service.AccessoryInformation)
      .setCharacteristic(this.api.hap.Characteristic.Manufacturer, this.deviceInfo.DeviceManufacturer)
      .setCharacteristic(this.api.hap.Characteristic.Model, this.deviceInfo.DeviceModel)
      .setCharacteristic(this.api.hap.Characteristic.SerialNumber, device);

    this.airQualityService = this.accessory.getService(this.api.hap.Service.AirQualitySensor) ||
                              this.accessory.addService(this.api.hap.Service.AirQualitySensor, 'WALL-E Sensor');

    this.airQualityService.getCharacteristic(this.api.hap.Characteristic.AirQuality)
      .onGet(() => {
        if (this.cachedAirQuality === null) {
          return this.api.hap.Characteristic.AirQuality.UNKNOWN;
        }
        return this.cachedAirQuality;
      });

    this.pm10Characteristic = this.airQualityService.getCharacteristic(this.api.hap.Characteristic.PM10Density) ||
                              this.airQualityService.addCharacteristic(this.api.hap.Characteristic.PM10Density);

    this.pm25Characteristic = this.airQualityService.getCharacteristic(this.api.hap.Characteristic.PM2_5Density) ||
                              this.airQualityService.addCharacteristic(this.api.hap.Characteristic.PM2_5Density);

    this.pollInterval = setInterval(() => this.updateState(), 5 * 60 * 1000);
    this.updateState();
  }

  async fetchData() {
    const url = `${this.apiEndpoint}/air/info/latest?device_name=${this.device}`;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 4000);
    try {
      const response = await fetch(url, { signal: controller.signal });
      if (!response.ok) {
        this.log.error(`HTTP error for ${this.device}: status=${response.status} url=${url}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.latest_info;
    } catch (error) {
      if (error.name === 'AbortError') {
        this.log.error(`Timeout fetching data for ${this.device}: request exceeded 4s (url=${url})`);
      } else {
        this.log.error(`Error fetching data for ${this.device}: ${error.message} (url=${url})`);
      }
      return null;
    } finally {
      clearTimeout(timeout);
    }
  }

  async updateState() {
    this.log.debug(`Updating state for device: ${this.device}`);
    const data = await this.fetchData();
    if (!data) {
      return;
    }

    if (data.staleness) {
      this.log.warn(`Stale data for ${this.device}: age=${data.age}s`);
      this.airQualityService.updateCharacteristic(this.api.hap.Characteristic.StatusFault, true);
      return;
    }

    try {
      const airQuality = this.parseAirQuality(data);
      const pm10 = parseFloat(data.PM10);
      const pm25 = parseFloat(data.PM25);

      this.cachedAirQuality = airQuality;
      this.cachedPM10 = pm10;
      this.cachedPM25 = pm25;

      this.airQualityService.updateCharacteristic(this.api.hap.Characteristic.AirQuality, airQuality);
      this.pm10Characteristic.updateValue(pm10);
      this.pm25Characteristic.updateValue(pm25);
      this.airQualityService.updateCharacteristic(this.api.hap.Characteristic.StatusFault, false);

      this.log.debug(`Updated ${this.device}: quality=${airQuality}, PM10=${pm10}, PM25=${pm25}`);

      if (parseInt(data.code, 10) >= 4) {
        this.log.warn(`Poor air quality for ${this.device}: code=${data.code}`);
      }
    } catch (error) {
      this.log.error(`Error updating air quality for ${this.device}: ${error}`);
    }
  }

  parseAirQuality(data) {
    const code = parseInt(data.code, 10);
    switch (code) {
      case 1: return this.api.hap.Characteristic.AirQuality.EXCELLENT;
      case 2: return this.api.hap.Characteristic.AirQuality.GOOD;
      case 3: return this.api.hap.Characteristic.AirQuality.FAIR;
      case 4: return this.api.hap.Characteristic.AirQuality.INFERIOR;
      case 5: return this.api.hap.Characteristic.AirQuality.POOR;
      default:
        this.log.warn(`Unknown air quality code for device ${this.device}: ${code}`);
        return this.api.hap.Characteristic.AirQuality.UNKNOWN;
    }
  }
}
