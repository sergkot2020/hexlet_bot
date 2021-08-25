import asyncpg
import logging

logger = logging.getLogger(__name__)


class Db:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.pool = None

    async def create_conn_pool(self, *, min_size=0, max_size=10):
        self.pool = await asyncpg.create_pool(
            host=self.params.get('host'),
            port=self.params.get('port'),
            database=self.params.get('database'),
            user=self.params.get('user'),
            password=self.params.get('password'),
            min_size=min_size,
            max_size=max_size,
        )
        logger.info('Database connected')
