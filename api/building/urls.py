from pathlib import Path

from shared.base.urls import BaseURL


class BuildingURL(BaseURL):
    """Building URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buildings_list: str = '/'
        self.building_create: str = '/'
        self.building_detail: str = '/{uuid}/'


building_url = BuildingURL(Path(__file__).parent.parent.name)
