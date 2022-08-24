import logging
from .message import (
    MessageQuery,
    MessagePower,
    MessageStart,
    MessageDAResponse
)
from ...core.device import MiedaDevice
from ...backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    start = "start"
    washing_data = "washing_data"
    progress = "progress"
    time_remaining = "time_remaining"


class MideaDADevice(MiedaDevice):
    def __init__(
            self,
            name: str,
            device_id: int,
            ip_address: str,
            port: int,
            token: str,
            key: str,
            protocol: int,
            model: str
    ):
        super().__init__(
            name=name,
            device_id=device_id,
            device_type=0xDA,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model
        )
        self._attributes = {
            DeviceAttributes.power: False,
            DeviceAttributes.start: False,
            DeviceAttributes.washing_data: bytearray([]),
            DeviceAttributes.progress: "Unknown",
            DeviceAttributes.time_remaining: None
        }

    def build_query(self):
        return [MessageQuery()]

    def process_message(self, msg):
        message = MessageDAResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        progress = ["Idle", "Spin", "Rinse", "Wash",
                    "Weight", "Unknown", "Dry", "Soak"]
        for status in self._attributes.keys():
            if hasattr(message, status.value):
                if status == DeviceAttributes.progress:
                    self._attributes[status] = progress[getattr(message, status.value)]
                else:
                    self._attributes[status] = getattr(message, status.value)
                new_status[status.value] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.power:
            message = MessagePower()
            message.power = value
            self.build_send(message)
        elif attr == DeviceAttributes.start:
            message = MessageStart()
            message.start = value
            message.washing_data = self._attributes[DeviceAttributes.washing_data]
            self.build_send(message)


class MideaAppliance(MideaDADevice):
    pass