import asyncpg
from typing import Any, List, Dict, Tuple
from app.services.database.database_client import DatabaseClient


class AsyncPostgresClient(DatabaseClient):
    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 5):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self.pool: asyncpg.Pool = None  # type: ignore

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            dsn=self.dsn, min_size=self.min_size, max_size=self.max_size
        )

    async def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def execute(self, query: str, params: Tuple = ()) -> int:
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *params)
            # asyncpg's execute() returns a string like 'UPDATE 3'
            affected = int(result.split()[-1]) if result.split()[-1].isdigit() else 0
            return affected

    async def close(self):
        await self.pool.close()
