"""Presentation helpers. Never mutate plans or recorded history."""
from datetime import date


def nice_date(iso: str) -> str:
    day = date.fromisoformat(iso)
    return f'{day:%a, %b} {day.day}'


def nice_range(start: str, end: str) -> str:
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first.year != last.year:
        return f'{first:%b} {first.day}, {first.year} – {last:%b} {last.day}, {last.year}'
    if first.month != last.month:
        return f'{first:%b} {first.day} – {last:%b} {last.day}'
    return f'{first:%b} {first.day} – {last.day}'


def friendly_rows(rows):
    return [{key: nice_date(value) if key == 'Date' else value for key, value in row.items()} for row in rows]
