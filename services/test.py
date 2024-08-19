import asyncio
from datetime import datetime
from typing import Callable

from api.actions.metrics_queries import _add_new_metrics
from api.actions.query_url_merge import _get_approach_query
from db.models import QueryUrlsMerge, QueryUrlsMergeLogs
from db.session import async_session

from db.utils import add_last_update_date, get_last_update_date
from services.search_competitors_async import run_bash_async

date_format = "%Y-%m-%d"

START_DATE = datetime.now().date()


# Получаем список подходящих запросов из бд и формируем queries.txt
async def get_approach_query(session: Callable):
    res = await _get_approach_query(session)
    res = res[:100]
    with open("queries.txt", "w", encoding="utf-8") as f:
        for cursor, query in enumerate(res):
            if cursor < len(res) - 1:
                f.write(f"{query[0]}\n")
            else:
                f.write(f"{query[0]}")


async def record_to_merge_db(session: Callable):
    with open("results_main_domain_async.txt", "r", encoding="utf-8") as f:
        values = {}
        values_to_db = []
        lines = [line.strip() for line in f.readlines()]
        for elem in range(3, len(lines)):
            url, query = lines[elem].split()[0], ' '.join(lines[elem].split()[1:])
            if url not in values:
                values[url] = []
            values[url].append(query)
        for key, value in values.items():
            values_to_db.append(QueryUrlsMerge(url=key, queries=value, date=START_DATE))
        last_update_date = await get_last_update_date(async_session, QueryUrlsMerge)
        if not last_update_date:
            last_update_date = datetime.strptime("1900-01-01", date_format)
        if START_DATE > last_update_date.date():
            await _add_new_metrics(values_to_db, session)
            await add_last_update_date(session, QueryUrlsMergeLogs, START_DATE)


async def main():
    print("Начало выполнения")
    await get_approach_query(async_session)
    curr = datetime.now()
    await run_bash_async()
    print("result main create")
    await record_to_merge_db(async_session)
    print("Скрипт успешно выполнен")


if __name__ == "__main__":
    asyncio.run(main())