"""Curated prototype activities and deterministic puzzle bank."""
YOGA = [
    ('Chair pose', 'Supported mini chair pose', 'Seated gentle leg press into the floor'),
    ('Warrior II', 'Short stance with chair support', 'Seated warrior arm reach'),
    ('Low lunge', 'Small supported split stance', 'Seated alternating leg extension'),
    ('Bridge', 'Small comfortable bridge on a mat', 'Seated gentle glute squeeze'),
    ('Cat-cow', 'Gentle hands-and-knees cat-cow', 'Seated gentle cat-cow'),
]


def yoga_content(profile, supported):
    limited = supported or bool(profile['limits'])
    return [{'id': str(i), 'name': name, 'version': seated if limited else standard,
             'cue': 'Use a comfortable range, breathe normally, and stop if painful. Use a stable chair; do not force a stretch.',
             'badge': 'Moderate', 'source': 'Yoga in older adults, IJBNPA 2019; yoga and frailty, Annals of Internal Medicine 2023'}
            for i, (name, standard, seated) in enumerate(YOGA)]


def puzzles():
    bank = []
    for level in range(1, 5):
        for index in range(6):
            start = index + 1
            if level == 1:
                step = index + 2
                values = [start + step * j for j in range(5)]
                reason = f'Add {step} each time.'
            elif level == 2:
                factor = 2 + index % 2
                values = [start * factor ** j for j in range(5)]
                reason = f'Multiply by {factor} each time.'
            elif level == 3:
                values = [(start + j) ** 2 for j in range(5)]
                reason = 'These are consecutive square numbers.'
            else:
                values = [start, start + 1]
                for _ in range(3):
                    values.append(values[-1] + values[-2])
                reason = 'Add the previous two numbers.'
            bank.append({'id': f'{level}-{index}', 'level': level,
                         'question': ', '.join(map(str, values[:4])) + ', ?',
                         'answer': values[4], 'explanation': reason})
    return bank

PUZZLES = puzzles()


def next_level(level, answers):
    if len(answers) >= 3 and all(answers[-3:]):
        return min(4, level + 1)
    if len(answers) >= 2 and not any(answers[-2:]):
        return max(1, level - 1)
    return level
