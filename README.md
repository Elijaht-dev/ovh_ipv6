# OVH IPv6 DynHost Updater for Home Assistant

This custom integration for Home Assistant allows you to automatically update your OVH DNS records with your current IPv6 address using OVH's DynHost service.

## Features

- Automatic IPv6 address detection
- Periodic DNS record updates (every 15 minutes)
- Easy configuration through the Home Assistant UI
- Uses OVH's official DynHost service
- Supports both A (IPv4) and AAAA (IPv6) records

## Prerequisites

1. An OVH account with a registered domain
2. DynHost enabled for your domain
3. A DynHost username and password
4. The hostname you want to update

## Installation

### HACS (Recommended)

[![Opens your Home Assistant instance and adds a repository to the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Elijaht-dev&repository=ovh_ipv6&category=integration)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/Elijaht-dev/ovh_ipv6`
6. Select category: "Integration"
7. Click "Add"
8. Find "OVH IPv6 DynHost" in the integration list and install it

### Manual Installation

1. Download the latest release from the repository
2. Copy the `custom_components/ovh_ipv6` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Setting up DynHost in OVH

1. Log into your OVH Control Panel
2. Navigate to your domain's DNS zone
3. Click on the "DynHost" tab
4. Create a new DynHost user by clicking "Manage access" and "Create an identifier"
5. Note down the username and password
6. Add a new DynHost record for the hostname you want to update

### Setting up the Integration

1. In Home Assistant, go to Configuration > Integrations
2. Click the "+ ADD INTEGRATION" button
3. Search for "OVH IPv6 DynHost"
4. Enter your:
   - DynHost Username
   - DynHost Password
   - Hostname to update (e.g., "dynamic.example.com")

## Troubleshooting

### Common Issues

- **Invalid authentication credentials**: Double-check your DynHost username and password
- **Cannot connect**: Verify your internet connection and that the DynHost service is accessible
- **No IPv6 address detected**: Ensure your network has IPv6 connectivity

### Logs

To view the integration's logs, add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.ovh_ipv6: debug
```

## Contributing

Feel free to contribute to this project by:
- Reporting issues
- Suggesting new features
- Creating pull requests

## License

This project is licensed under the Apache License, Version 2.0 (the "License") - see the LICENSE file for details.
