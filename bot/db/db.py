import logging
from datetime import datetime

import asyncpg

from bot.const import DAY_MAP

logger = logging.getLogger(__name__)


class Db:
    def __init__(
            self,
            *,
            user,
            db_name,
            password,
            host,
            port=5432,
    ):
        self.user = user
        self.db_name = db_name
        self.password = password
        self.host = host
        self.port = port
        self.pool = None

    async def create_conn_pool(self, *, min_size=0, max_size=10):
        self.pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            database=self.db_name,
            user=self.user,
            password=self.password,
            min_size=min_size,
            max_size=max_size,
        )
        logger.info('Database connected')

    async def add_chat_if_not_exist(
            self,
            *,
            chat_id: int,
            title,
            gigagroup=False,
            megagroup=True,
    ):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    '''\
insert into chat (telegram_id, gigagroup, megagroup, title)
values ($1, $2, $3, $4)
on conflict (telegram_id) do update 
    set title = excluded.title    
returning id      
''',
                    chat_id,
                    gigagroup,
                    megagroup,
                    title,
                )
                id_ = row['id']
                await conn.execute(
                    '''\
insert into chat_settings (chat_id)
values ($1)
on conflict do nothing 
''',
                    id_,
                )
                return id_

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
        row = await self.pool.fetchrow(
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
on conflict (telegram_id)  do update
     set first_name = excluded.first_name,
         last_name = excluded.last_name,
         username = excluded.username,
         phone = excluded.phone
returning id
''',
            telegram_id,
            is_bot,
            first_name,
            last_name,
            lang_code,
            phone,
            username,
        )
        return row['id']

    async def add_chat_user_relation_if_not_exist(self, chat_id, user_id):
        await self.pool.execute(
            '''\
insert into chat_user_relation (chat_id, user_id)
values ($1, $2)
on conflict (chat_id, user_id) do nothing 
''',
            chat_id,
            user_id,
        )

    async def add_report(self, chat_id, user_id, text):
        await self.pool.execute(
            '''\
insert into report (
    chat_id, 
    user_id, 
    text 
)
values ($1, $2, $3)
''',
            chat_id,
            user_id,
            text,
        )

    async def get_chat_id(self, telegram_id):
        row = await self.pool.fetchrow(
            '''\
select id
from chat
where telegram_id = $1
''',
            telegram_id
        )
        if row:
            return row['id']

    async def get_user_id(self, telegram_id):
        row = await self.pool.fetchrow(
            '''\
select id
from "user"
where telegram_id = $1
''',
            telegram_id
        )
        if row:
            return row['id']

    async def get_settings(self, day: int, notice_type: str, meeting_date: datetime):
        return await self.pool.fetch(
            f'''\
select cs.chat_id,
       c.telegram_id,
       cs.notice_msg,
       cs.congratulation_msg,
       cs.censure_msg,
       m.users
from chat_settings cs
left join chat c on c.id = cs.chat_id
left join (
    select *
    from notice_log
    where day = $1
        and notice_type = $2
        and date_trunc('day', created) = date_trunc('day', now())
    )  nl on c.id= nl.chat_id
left join (
    select *
    from meeting
    where date_trunc('day', start_ts) = date_trunc('day',$3::timestamptz)
    ) m on m.chat_id = cs.chat_id
where cs.{DAY_MAP[day]} = true
    and nl.created isnull
order by chat_id            
''',
            day,
            notice_type,
            meeting_date,
        )

    async def add_notice_log(self, chat_id, day, notice_type):
        await self.pool.execute(
            '''\
insert into notice_log (chat_id, day, notice_type) 
values ($1, $2, $3)
''',
            chat_id,
            day,
            notice_type,
        )

    async def start_meeting(self, chat_id):
        await self.pool.execute(
            '''\
insert into meeting (chat_id)
values ($1)
''',
            chat_id
        )

    async def add_user_to_meeting(self, chat_id, user_id):
        await self.pool.execute(
            '''\
update meeting
    set users = array_prepend($1, users)
where chat_id = $2
    and date_trunc('day', start_ts) = date_trunc('day', now())
''',
            user_id,
            chat_id,
        )

    async def get_users(self, chat_id):
        await self.pool.fetch(
            '''\
select
       u.id,
       u.telegram_id,
       u.first_name,
       u.last_name,
       u.username,
       c.telegram_id as chat_telegram_id,
       c.title
from "user" u
left join chat_user_relation cur on cur.user_id = u.id
left join chat c on c.id = cur.chat_id
where is_bot = false
    and cur.chat_id = $1
''',
            chat_id
        )

    async def get_all_users(self):
        return await self.pool.fetch(
            '''\
select 
    telegram_id,
    username
from "user"
''',
        )

    async def update_chat_settings(
            self,
            chat_id,
            monday=True,
            tuesday=False,
            wednesday=False,
            thursday=False,
            friday=False,
            saturday=False,
            sunday=False,
    ):
        await self.pool.execute(
            '''\
update chat_settings
set monday = $1,
    tuesday = $2,
    wednesday = $3,
    thursday = $4,
    friday = $5,
    saturday = $6,
    sunday = $7
where chat_id = $8
''',
            monday,
            tuesday,
            wednesday,
            thursday,
            friday,
            saturday,
            sunday,
            chat_id,
        )
