### CasaPAT Homebridge App
## Homebridge Config
You will need to add the following to your config file found in ~/.homebridge/config.json
```
"platforms": [
        {
            "platform": "CasaPAT",
            "name": "CasaPAT",
            "apiEndpoint": "http://pat.local:5000"
        }
    ]
```