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

    async def add_chat_if_not_exist(
            self,
            *,
            chat_id: int,
            gigagroup=False,
            megagroup=True,
    ):
        await self.pool.execute(
            '''\
insert into chat (telegram_id, gigagroup, megagroup)
values ($1, $2, $3)
on conflict do nothing            
''',
            chat_id,
            gigagroup,
            megagroup,
        )

    async def add_user_if_not_exist(
            self,
            *,
            telegram_id,
            is_bot=False,
            first_name=None,
            last_name=None,
            lang_code=None,
            phone=None,
            username=None,
    ):
        await self.pool.execute(
            '''\
insert into "user" (
    telegram_id, 
    is_bot, 
    first_name, 
    last_name, 
    lang_code, 
    phone, 
    username
)
values ($1, $2, $3, $4, $5, $6, $7)
on conflict do nothing
''',
            telegram_id,
            is_bot,
            first_name,
            last_name,
            lang_code,
            phone,
            username,
        )

