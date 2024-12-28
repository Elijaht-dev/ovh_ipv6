# OVH IPv6 DNS Updater for Home Assistant

This custom integration for Home Assistant allows you to automatically update your OVH DNS records with your current IPv6 address, effectively creating a dynamic DNS service for IPv6.

## Features

- Automatic IPv6 address detection
- Periodic DNS record updates (every 15 minutes)
- Easy configuration through the Home Assistant UI
- Supports OVH DNS API

## Prerequisites

1. An OVH account with a registered domain
2. OVH API credentials (Application Key, Application Secret, and Consumer Key)
3. The DNS record ID for the record you want to update

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/Elijaht-dev/ovh_ipv6`
6. Select category: "Integration"
7. Click "Add"
8. Find "OVH IPv6 DNS" in the integration list and install it

### Manual Installation

1. Download the latest release from the repository
2. Copy the `custom_components/ovh_ipv6` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Getting OVH API Credentials

1. Go to [OVH API Create App](https://eu.api.ovh.com/createApp/)
2. Log in with your OVH account
3. Create a new application
4. Note down the Application Key and Application Secret
5. Generate a Consumer Key using the provided credentials

### Finding Your DNS Record ID

1. Log into your OVH control panel
2. Navigate to your domain's DNS zone
3. Find the AAAA record you want to update
4. Note down the DNS zone name and record ID

### Setting up the Integration

1. In Home Assistant, go to Configuration > Integrations
2. Click the "+ ADD INTEGRATION" button
3. Search for "OVH IPv6 DNS"
4. Enter your:
   - Application Key
   - Application Secret
   - Consumer Key
   - DNS Zone (your domain name)
   - DNS Record ID

## Troubleshooting

### Common Issues

- **Invalid authentication credentials**: Double-check your OVH API credentials
- **DNS zone or record ID not found**: Verify your DNS zone name and record ID
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

This project is licensed under the MIT License - see the LICENSE file for details.