import asyncio

import yaml

from abc import ABC
from typing import List
from uvicorn import Config, Server


class APP(ABC):
    def __init__(self):
        self.props = {}
        self._load_properties()

    def _load_properties(self):
        properties_file = 'resources/properties.yml'
        with open(properties_file, 'r', encoding='UTF-8') as yml:
            self.props = yaml.safe_load(yml)

            self.host           : str = self.props['SERVER']['HOST']
            self.port           : int = self.props['SERVER']['PORT']
            self.cors_origins   : List[str] = self.props['SERVER']['CORS_ORIGINS']
            self.prefix         : str = self.props['SERVER']['PREFIX']

            self.jwt_header     : str = self.props['JWT']['HEADER']
            self.jwt_secret_key : str = self.props['JWT']['SECRET_KEY']

    def _server_load(self, app) -> Server:
        self._loop = asyncio.get_event_loop()
        config = Config(app=app,
                        host=self.host,
                        port=self.port,
                        loop=self._loop)
        return Server(config)
