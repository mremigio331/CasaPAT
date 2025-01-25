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

sudo npm link
sudo npm link casaPat
sudo systemctl restart homebridge