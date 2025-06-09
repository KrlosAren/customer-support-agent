# app/services/database/database_client.py

from abc import ABC, abstractmethod
from typing import Any, List, Dict, Tuple


class DatabaseClient(ABC):
    @abstractmethod
    async def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def execute(self, query: str, params: Tuple = ()) -> int:
        pass
