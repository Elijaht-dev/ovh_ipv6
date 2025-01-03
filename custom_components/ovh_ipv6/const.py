"""Constants for the OVH IPv6 integration."""
from datetime import timedelta

DOMAIN = "ovh_ipv6"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_HOSTNAME = "hostname"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_INTERVAL = timedelta(minutes=15)
DYNHOST_UPDATE_URL = "https://dns.eu.ovhapis.com/nic/update"
