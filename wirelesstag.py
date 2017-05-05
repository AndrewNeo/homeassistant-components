import logging
from homeassistant.helpers import discovery
from homeassistant.const import CONF_API_KEY

from homeassistant.util import Throttle
from datetime import timedelta

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['requests==2.13.0']

DOMAIN = "wirelesstag"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_API_KEY): cv.string
    })
}, extra=vol.ALLOW_EXTRA)


WIRELESSTAG = None
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

_LOGGER = logging.getLogger(__name__)


class WirelessTagService(object):
    def __init__(self, api_key):
        self.api_key = api_key

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def updateTagList(self):
        _LOGGER.debug("Fetching tag data")
        import requests
        r = requests.post("https://www.mytaglist.com/ethClient.asmx/GetTagList", headers={
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json"
        }, data="{}")
        r.raise_for_status()
        self.tags = r.json()["d"]

    def getTags(self):
        return self.tags

    def getTag(self, uuid):
        return next((item for item in self.tags if item["uuid"] == uuid), None)


def setup(hass, config):
    api_key = config[DOMAIN][CONF_API_KEY]
    if api_key is None:
        _LOGGER.warning("API key is unset, will not function")
        return False

    global WIRELESSTAG
    WIRELESSTAG = WirelessTagService(api_key)

    discovery.load_platform(hass, "sensor", DOMAIN, {}, config)
    return True
