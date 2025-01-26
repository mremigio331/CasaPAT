import { CasaPAT } from './platform.js';

export default (homebridge) => {
  homebridge.registerPlatform(
    'homebridge-casapat',
    'CasaPAT',
    CasaPAT
  );
};
