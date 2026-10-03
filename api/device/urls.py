from pathlib import Path

from shared.base.urls import BaseURL


class DeviceURL(BaseURL):
    """Device URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices_list: str = '/'
        self.device_create: str = '/'
        self.device_detail: str = '/{uuid}/'
        self.device_update: str = '/{uuid}/'
        self.device_delete: str = '/{uuid}/'
        self.device_api_key_create: str = '/{uuid}/api-key/'
        self.device_api_key_delete: str = '/{uuid}/api-key/'


device_url = DeviceURL(Path(__file__).parent.parent.name)
