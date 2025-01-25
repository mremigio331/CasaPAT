import { WALL_E } from './src/platform.js';

console.log('Loading CasaPat...');

const log = {
  info: console.log,
  warn: console.warn,
  error: console.error,
};

const config = {
  apiEndpoint: 'http://pat.local:5000'
};

const api = {
  hap: {
    Service: {
      AirQualitySensor: class {
        constructor(name) {
          this.name = name;
        }
      },
      ContactSensor: class {
        constructor(name) {
          this.name = name;
        }
      },
      BatteryService: class {
        constructor(name) {
          this.name = name;
        }
      },
      AccessoryInformation: class {}
    },
    Characteristic: {
      AirQuality: {
        EXCELLENT: 1,
        GOOD: 2,
        FAIR: 3,
        INFERIOR: 4,
        POOR: 5,
        UNKNOWN: 0
      },
      ContactSensorState: {
        CONTACT_DETECTED: 1, // Door closed
        CONTACT_NOT_DETECTED: 0 // Door open
      },
      BatteryLevel: class {},
      Manufacturer: class {},
      Model: class {},
      SerialNumber: class {},
      PM10Density: class {},
      PM2_5Density: class {}
    },
    uuid: {
      generate: (id) => `uuid-${id}`
    },
    platformAccessory: class {
      constructor(name, uuid) {
        this.displayName = name;
        this.UUID = uuid;
        this.context = {};
      }

      getService(service) {
        if (!this.services) {
          this.services = {};
        }
        if (!this.services[service]) {
          this.services[service] = new service(this.displayName);
        }
        return this.services[service];
      }

      setCharacteristic() {
        return this;
      }

      addService(service, name) {
        this.services = this.services || {};
        this.services[name] = new service(name);
        return this.services[name];
      }

      getCharacteristic() {
        return {
          on: (event, callback) => {}
        };
      }
    }
  },
  registerPlatformAccessories: (pluginName, platformName, accessories) => {
    console.log('Registering accessories:', accessories.map(a => a.displayName));
  },
  on: (event, callback) => {
    if (event === 'didFinishLaunching') {
      callback();
    }
  }
};

const platform = new WALL_E(log, config, api);

console.log('Plugin loaded successfully');
