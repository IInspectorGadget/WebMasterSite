import asyncio
from datetime import datetime, timedelta
from typing import Callable

from api.actions.metrics_queries import _add_new_metrics
from api.actions.query_url_merge import _get_approach_query
from bash_script.bash_script_runner import run_bash_script
from db.models import QueryUrlsMerge, QueryUrlsMergeLogs
from db.session import async_session

from db.utils import add_last_update_date

date_format = "%Y-%m-%d"

START_DATE = datetime.now().date()


# Получаем список подходящих запросов из бд и формируем queries.txt
async def get_approach_query(session: Callable):
    res = await _get_approach_query(session)
    with open("../bash_script/queries.txt", "w", encoding="utf-8") as f:
        for cursor, query in enumerate(res):
            if cursor < len(res) - 1:
                f.write(f"{query[0]}\n")
            else:
                f.write(f"{query[0]}")


async def record_to_merge_db(session: Callable):
    with open("../bash_script/results_main_domain.txt", "r", encoding="utf-8") as f:
        values = {}
        values_to_db = []
        lines = [line.strip() for line in f.readlines()]
        for elem in range(3, len(lines), 2):
            url, query = lines[elem].split()[0], ' '.join(lines[elem].split()[1:])
            if url not in values:
                values[url] = []
            values[url].append(query)
        for key, value in values.items():
            values_to_db.append(QueryUrlsMerge(url=key, queries=value))
        await _add_new_metrics(values_to_db, session)
        await add_last_update_date(session, QueryUrlsMergeLogs, START_DATE)


async def main():
    # await get_approach_query(async_session)
    #
    # await run_bash_script()
    await record_to_merge_db(async_session)


if __name__ == "__main__":
    asyncio.run(main())