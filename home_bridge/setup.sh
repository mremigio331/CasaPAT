#! /bin/bash

sudo apt update
sudo apt install npm

sudo apt install curl -y

curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g homebridge

npm install rimraf --save-dev
npm run build

sudo hb-service link

sudo cp -r . /var/lib/homebridge/node_modules/homebridge-casapat
sudo chown -R homebridge:homebridge /var/lib/homebridge/node_modules/homebridge-casapat
sudo systemctl restart homebridge