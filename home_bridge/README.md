### CasaPAT Homebridge App

## Homebridge Config
You will need to add the following to your config file found in `/var/lib/homebridge/config.json`:
```json
"platforms": [
        {
            "platform": "CasaPAT",
            "name": "CasaPAT",
            "apiEndpoint": "http://pat.local:5000"
        }
    ]
```

---

## Troubleshooting

### Plugin not connecting — "No plugin was found for the platform CasaPAT"

Homebridge logs this generic message whenever the plugin fails to load. Work through the checks below in order.

#### 1. Check for missing dependencies

The plugin must be built and all dependencies installed before Homebridge can load it.

```bash
cd /home/pi/CasaPAT/home_bridge
npm install      # installs all dependencies including express
npm run build    # compiles src/ → dist/
```

To verify the plugin loads cleanly with Homebridge's own Node binary:
```bash
/opt/homebridge/bin/node -e "require('/home/pi/CasaPAT/home_bridge/index.js'); console.log('OK')"
```
If this prints `OK`, the plugin code is fine. If it throws (e.g. `Cannot find module 'express'`), a dependency is missing — run `npm install`.

#### 2. Check the symlink

The plugin must be symlinked into Homebridge's plugin directory:
```bash
ls -la /var/lib/homebridge/node_modules/homebridge-casapat
# should show: ... -> /home/pi/CasaPAT/home_bridge
```

If the symlink is missing, re-link it:
```bash
cd /home/pi/CasaPAT/home_bridge
sudo hb-service link
```

#### 3. Check `/var/lib/homebridge/package.json`

Homebridge v2 with `--strict-plugin-resolution` reads this file to know which plugins to load. `homebridge-casapat` must be listed:
```bash
cat /var/lib/homebridge/package.json
```

If it is missing from `dependencies`, add it:
```bash
sudo bash -c 'cat /var/lib/homebridge/package.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
d[\"dependencies\"][\"homebridge-casapat\"] = \"^1.0.0\"
print(json.dumps(d, indent=2))
" > /tmp/pkg.json && cp /tmp/pkg.json /var/lib/homebridge/package.json'
```

#### 4. Check `/home/pi` directory permissions (most likely cause)

The `homebridge` service runs as the `homebridge` user. If `/home/pi` has `700` permissions (the Raspberry Pi OS default), the `homebridge` user cannot traverse the path to the plugin. Homebridge silently drops the plugin with only a `log.debug` message — it will **not** appear in normal logs.

Check:
```bash
ls -la /home/ | grep pi
# bad:  drwx------  pi  pi  ...
# good: drwx--x--x  pi  pi  ...
```

Fix (adds traverse-only access for others — does not expose your home directory listing):
```bash
chmod o+x /home/pi
```

Verify the `homebridge` user can now reach the plugin:
```bash
sudo -u homebridge stat /home/pi/CasaPAT/home_bridge
# should print file info, not "Permission denied"
```

#### 5. Restart and confirm

```bash
sudo hb-service restart
sudo tail -30 /var/lib/homebridge/homebridge.log
```

A successful load looks like:
```
[CasaPAT] Initializing CasaPAT platform...
[CasaPAT] Initializing CasaPat...
[CasaPAT] Webhook server started on port 8080
```

---

## Setup from Scratch

Run the setup script from the plugin directory:
```bash
cd /home/pi/CasaPAT/home_bridge
chmod +x setup.sh
./setup.sh
```

The script installs Node.js 22.x, Homebridge, all plugin dependencies, builds the plugin, and links it into Homebridge.

After running setup, also ensure `/home/pi` is traversable by the `homebridge` user (see step 4 above) and that `homebridge-casapat` is present in `/var/lib/homebridge/package.json` (see step 3 above). These two steps are not handled by the setup script.
