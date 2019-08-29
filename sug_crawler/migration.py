
import asyncio
import asyncpg
from sug_config import DB_NAME


async def init_db():
    print('crawler init_db started')
    connect = await asyncpg.connect(dsn=DB_NAME)

    tmp = await connect.execute('''drop table IF EXISTS keywords;''')
    print(tmp)

    await connect.execute(
        '''CREATE TABLE IF NOT EXISTS keywords(
            keyword_id SERIAL,
            keyword VARCHAR(128) UNIQUE NOT NULL);
        ''')

    try:
        res = await connect.execute(
            '''INSERT INTO keywords (keyword) 
            VALUES ($1), ($2)
            RETURNING keyword_id''', *("apple", "google"))
        print(res)
    except asyncpg.IntegrityConstraintViolationError as e:
        print(e)

    vals = await connect.fetch('select keyword from keywords limit 100')
    print([list(v.items()) for v in vals])


if __name__ == '__main__':
    print(DB_NAME)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
