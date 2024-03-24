import re
import click
from datetime import datetime, timedelta
import httpx


def get_rate(currency: str, date: datetime = datetime.today()) -> tuple[float, datetime]:
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
    return mid, date


def parse_date(date: str) -> datetime:
    match = re.match(r"(\d+).(\d+).(\d+)", date)
    if len(match.groups()[0]) == 4:
        year, month, day = map(int, match.groups())
    else:
        day, month, year = map(int, match.groups())
    return datetime(year=year, month=month, day=day)


@click.command()
@click.argument("currency")
@click.option("-d", "--date", "date")
def main(currency: str, date: str):
    date = parse_date(date) if date else datetime.today()
    rate, latest_available_date = get_rate(currency, date)
    print(rate, latest_available_date.strftime("%Y-%m-%d"))


if __name__ == '__main__':
    main()
