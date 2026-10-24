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


def inert_chunks(text):
    """Escape Markdown and HTML before write_stream receives filtered coach text."""
    import html
    safe = html.escape(text)
    safe = ''.join(chr(92) + char if char in chr(92) + '`*_{}[]()#+.!|>~-' else char for char in safe)
    for word in safe.split(' '):
        yield word + ' '


def week_ics(plan):
    """Deterministic all-day calendar, folded at 75 UTF-8 octets (RFC 5545)."""
    from datetime import timedelta
    from uuid import uuid5, NAMESPACE_URL
    labels = {'strength': 'Strength & balance', 'yoga': 'Yoga', 'brain': 'Brain games', 'relaxation': 'Relaxation'}
    def fold(line):
        parts, current = [], ''
        for char in line:
            if len((current + char).encode('utf-8')) > 75:
                parts.append(current)
                current = ' '
            current += char
        return '\r\n'.join(parts + [current])
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//ZINC//Weekly activities//EN', 'CALSCALE:GREGORIAN']
    for activity in plan['activities']:
        day = date.fromisoformat(activity['date'])
        uid = uuid5(NAMESPACE_URL, 'zinc:activity:' + activity['id'])
        lines += ['BEGIN:VEVENT', f'UID:{uid}@zinc.local', f'DTSTAMP:{day:%Y%m%d}T000000Z',
                  f'DTSTART;VALUE=DATE:{day:%Y%m%d}', f'DTEND;VALUE=DATE:{day + timedelta(days=1):%Y%m%d}',
                  'SUMMARY:ZINC · ' + labels[activity['section']],
                  f'DESCRIPTION:Estimated duration: {int(activity["minutes"])} minutes. General wellness activity.',
                  'END:VEVENT']
    return '\r\n'.join(fold(line) for line in lines + ['END:VCALENDAR']) + '\r\n'
