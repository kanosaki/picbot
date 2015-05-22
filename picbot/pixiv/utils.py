
from datetime import datetime

DATE_FORMAT = '%Y-%m-%d'

def format_date(dt: datetime) -> str:
    return dt.strftime(DATE_FORMAT)


def parse_date(expr: str) -> datetime:
    return datetime.strptime(expr, DATE_FORMAT)
