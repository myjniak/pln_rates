import re
import click
from datetime import datetime, timedelta
import httpx


def list_all_currencies() -> list[str]:
    url = "https://api.nbp.pl/api/exchangerates/tables/a/"
    response = httpx.get(url)
    response.raise_for_status()
    currencies = [rate["code"] for rate in response.json()[0]["rates"]]
    return currencies


def get_rate(currency: str, date: datetime = datetime.today()) -> tuple[float, datetime, str]:
    while True:
        url = f"https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{date.strftime("%Y-%m-%d")}"
        response = httpx.get(url)
        if response.status_code == 404:
            date = date - timedelta(days=1)
        elif response.status_code == 200:
            break
        else:
            response.raise_for_status()
    mid = response.json()["rates"][0]["mid"]
    table = response.json()["rates"][0]["no"]
    return mid, date, table


def parse_date(date: str) -> datetime:
    match = re.match(r"(\d+).(\d+).(\d+)", date)
    if len(match.groups()[0]) == 4:
        year, month, day = map(int, match.groups())
    else:
        day, month, year = map(int, match.groups())
    return datetime(year=year, month=month, day=day)


@click.group()
def cli():
    pass


@cli.command()
def list_currencies():
    all_currencies = list_all_currencies()
    for cur in all_currencies:
        print(cur)


@cli.command()
@click.argument("currency")
@click.option("-d", "--date", "date")
def get(currency: str, date: str):
    """Gets rate for an invoice created at a given date.
    It first looks at provided date minus 1 day, and then looks further back to the past
    if the given currency rate wasn't published for that day.
    """
    date = parse_date(date) if date else datetime.today()
    rate, latest_available_date, table_id = get_rate(currency, date - timedelta(days=1))
    print(",".join((str(rate), latest_available_date.strftime("%Y-%m-%d"), table_id)))


if __name__ == '__main__':
    cli()
