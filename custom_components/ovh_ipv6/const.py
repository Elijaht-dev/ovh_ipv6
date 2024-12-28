"""Constants for the OVH IPv6 integration."""
from datetime import timedelta

DOMAIN = "ovh_ipv6"
CONF_OVH_AK = "ovh_ak"
CONF_OVH_AS = "ovh_as"
CONF_OVH_CK = "ovh_ck"
CONF_DNSZONE = "dnszone"
CONF_DNSID = "dnsid"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_INTERVAL = timedelta(minutes=15)
