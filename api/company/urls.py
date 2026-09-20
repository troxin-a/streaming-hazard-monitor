from pathlib import Path

from shared.base.urls import BaseURL


class CompanyURL(BaseURL):
    """Company URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.companies_list: str = '/'
        self.company_create: str = '/'
        self.company_detail: str = '/{uuid}/'
        self.company_update: str = '/{uuid}/'
        self.company_delete: str = '/{uuid}/'


company_url = CompanyURL(Path(__file__).parent.parent.name)
