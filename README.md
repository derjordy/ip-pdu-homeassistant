# IP Smart PDU Integration for Home Assistant

Custom integration for IP Smart PDU devices (various manufacturers including Intellinet 163682).

## Features

- **8 Outlet Switches** - Control each outlet individually
- **Sensors:**
  - Temperature (°C)
  - Humidity (%)
  - Current (A)
  - Power (W) - calculated from current × configured voltage
- **Configurable voltage** (100V, 110V, 120V, 220V, 230V, 240V)
- **Dynamic device info** - reads model, firmware, MAC from device

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click "Integrations"
3. Click the three dots menu → "Custom repositories"
4. Add `https://github.com/derjordy/ip-pdu-homeassistant` as "Integration"
5. Search for "IP Smart PDU" and install
6. Restart Home Assistant

### Manual Installation

1. Copy `custom_components/intellinet_pdu` to your Home Assistant `config/custom_components/` folder
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "IP Smart PDU" or "Intellinet"
4. Enter:
   - IP Address of your PDU
   - Username (default: `admin`)
   - Password (default: `admin`)
   - Voltage (select your local grid voltage)

## Supported Devices

This integration works with various IP PDU devices that share the same web interface:

- Intellinet IP Smart PDU 163682
- Other rebranded versions with the same firmware

## Security Warning

These PDU devices have minimal security. The HTTP authentication only protects the main page - all other endpoints are unprotected. **Do not expose these devices to the internet.**

## License

MIT License
