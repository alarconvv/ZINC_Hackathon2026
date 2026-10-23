"""Read-only presentation data and SVG for the weekly progress board."""
from datetime import date, timedelta
from html import escape

LABELS = {'strength': 'Strength & balance', 'yoga': 'Yoga', 'brain': 'Brain games', 'relaxation': 'Relaxation'}


def summarize(plan, activity_sessions):
    activities = plan['activities']
    rows = [{'Date': a['date'], 'Section': LABELS[a['section']],
             'Status': activity_sessions.get(a['id'], {}).get('status', 'not started')} for a in activities]
    complete = sum(r['Status'] == 'completed' for r in rows)
    partial = sum(r['Status'] == 'partial' for r in rows)
    start = date.fromisoformat(plan['start_date'])
    days = [start + timedelta(days=i) for i in range(7)]
    daily = [sum(r['Status'] == 'completed' and r['Date'] == str(day) for r in rows) for day in days]
    sections = [{'name': label, 'done': sum(r['Status'] == 'completed' and r['Section'] == label for r in rows),
                 'total': sum(r['Section'] == label for r in rows)} for label in LABELS.values()]
    return {'rows': rows, 'done': complete, 'partial': partial, 'total': len(rows),
            'percent': round(100 * complete / len(rows)) if rows else 0,
            'days': days, 'daily': daily, 'sections': sections}


def date_range(plan):
    start = date.fromisoformat(plan['start_date'])
    end = start + timedelta(days=6)
    return f"{start.strftime('%b')} {start.day} – {end.strftime('%b')} {end.day}, {end.year}"


def activity_chart(board):
    """Daily completions: smooth joins at actual points, with an honest zero baseline."""
    values = board['daily']
    maximum = max(4, max(values, default=0))
    points = [(48 + i * 82, 168 - value / maximum * 130) for i, value in enumerate(values)]
    path = f'M {points[0][0]} {points[0][1]}'
    for (x0, y0), (x, y) in zip(points, points[1:]):
        middle = (x0 + x) / 2
        path += f' C {middle} {y0}, {middle} {y}, {x} {y}'
    grid = ''.join(f'<line x1="48" y1="{168-v/maximum*130}" x2="540" y2="{168-v/maximum*130}" stroke="#d8e6f3" stroke-dasharray="3 5"/><text x="26" y="{173-v/maximum*130}" text-anchor="middle">{v}</text>' for v in (0, maximum//2, maximum))
    labels = ''.join(f'<text x="{x}" y="200" text-anchor="middle">{day.strftime("%a")}</text><circle cx="{x}" cy="{y}" r="4" fill="#126bc5" stroke="white" stroke-width="2"/>' for (x,y), day in zip(points, board['days']))
    description = ', '.join(f'{day.strftime("%A")}: {value}' for day,value in zip(board['days'],values))
    return f'<svg class="activity-chart" viewBox="0 0 580 218" role="img" aria-label="Completed activities by scheduled day. {escape(description)}"><defs><linearGradient id="sea-fill" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#69b6f2" stop-opacity=".38"/><stop offset="1" stop-color="#69b6f2" stop-opacity=".03"/></linearGradient></defs><g fill="#526b84" font-family="sans-serif" font-size="13">{grid}<path d="{path} L 540 168 L 48 168 Z" fill="url(#sea-fill)"/><path d="{path}" fill="none" stroke="#126bc5" stroke-width="3"/>{labels}</g></svg>'


def feedback_rows(state, plan):
    activities = {a['id']: a for a in plan['activities']}
    names = {e['id']: e['name'] for e in plan['exercises']}
    rows = []
    for record in state['logs']['sessions']:
        if record.get('week') == plan['week']:
            activity = activities.get(record.get('activity_id'), {})
            rows.append({'Date': activity.get('date', 'Not recorded'), 'Activity': 'Strength & balance',
                         'Movement': names.get(record['exercise_id'], record['exercise_id']), 'Set or pose': record['set'],
                         'Pain': record['pain'], 'Effort': record['effort']})
    for session in state['activity_sessions'].values():
        if session['week'] == plan['week'] and session['section'] == 'yoga':
            for record in session['feedback']:
                rows.append({'Date': session['date'], 'Activity': 'Yoga', 'Movement': f"Pose {record['pose'] + 1}",
                             'Set or pose': record['pose'] + 1, 'Pain': record['pain'], 'Effort': record['effort']})
    return sorted(rows, key=lambda r: (r['Date'], r['Activity']))
