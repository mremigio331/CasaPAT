import { CasaPAT } from './platform.js';

export default (homebridge) => {
  homebridge.registerPlatform(
    'casaPAT',
    'casaPAT',
    CasaPAT
  );
};
