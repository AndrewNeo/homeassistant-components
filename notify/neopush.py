"""
Neopush platform for notify component.
"""
import logging

import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_DATA, ATTR_TITLE, ATTR_TITLE_DEFAULT,
    PLATFORM_SCHEMA, BaseNotificationService)
from homeassistant.const import CONF_API_KEY
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['requests==2.13.0']

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
})


# pylint: disable=unused-argument
def get_service(hass, config, discovery_info=None):
    """Get the Neopush notification service."""
    return NeoPushNotificationService(config[CONF_API_KEY])


class NeoPushNotificationService(BaseNotificationService):
    """Implement the notification service for NeoPush."""

    def __init__(self, api_key):
        """Initialize the service."""
        self.api_key = api_key
        self.NEOPUSH_URL = "https://projects.neocodenetworks.com/neopush/app/send"

    def send_message(self, message=None, **kwargs):
        import requests
        title = kwargs.get(ATTR_TITLE, ATTR_TITLE_DEFAULT)
        data = kwargs.get(ATTR_DATA)
        subchannel = None
        if data:
            subchannel = data.get("subchannel", None)

        headers = {"x-api-key": self.api_key}
        body = {"title": title, "body": message, "sub_channel": subchannel}
        r = requests.post(self.NEOPUSH_URL, headers=headers, json=body)

        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            _LOGGER.error("neopush send got error", e)
