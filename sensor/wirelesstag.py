import logging
from homeassistant.const import TEMP_CELSIUS, STATE_HOME, STATE_NOT_HOME, ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import Entity
from homeassistant.util.temperature import convert
from homeassistant.loader import get_component


_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    temp_unit = hass.config.units.temperature_unit

    svc = get_component("wirelesstag").WIRELESSTAG
    svc.updateTagList()

    devices = []
    for tag in svc.getTags():
        devices.append(WirelessTagSensor(svc, tag, temp_unit))

    add_devices(devices)


class WirelessTagSensor(Entity):
    def __init__(self, svc, tag, temp_unit):
        self.svc = svc
        self.tag = tag
        self.temp_unit = temp_unit

    @property
    def unique_id(self):
        return self.tag["uuid"]

    @property
    def name(self):
        return self.tag["name"]

# Save this for seperate prox sensor class
#    @property
#    def state(self):
#        return STATE_NOT_HOME if self.tag["OutOfRange"] else STATE_HOME

    @property
    def state(self):
        return round(convert(self.tag["temperature"], TEMP_CELSIUS, self.temp_unit), 1)

    @property
    def unit_of_measurement(self):
        return self.temp_unit

    @property
    def assumed_state(self):
        return not self.tag["alive"]

    @property
    def device_state_attributes(self):
        return {
            "humidity": "%d%%" % (round(self.tag["cap"]), ),
            "comment": self.tag["comment"],
            ATTR_BATTERY_LEVEL: "%d%%" % (self.tag["batteryRemaining"] * 100.0, )
        }

    def update(self):
        self.svc.updateTagList()
        self.tag = self.svc.getTag(self.tag["uuid"])
