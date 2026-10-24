import html
from pathlib import Path
import streamlit as st
import engine
import coach
from ui_helpers import nice_date, nice_range, friendly_rows

st.set_page_config(page_title='ZINC · Strength for the years ahead', page_icon='✳', layout='wide')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--ink:#12365b;--blue:#126bc5;--muted:#526b84}
html,body,.stApp{font-family:'DM Sans',sans-serif;line-height:1.6}
.stApp{color:white;background:radial-gradient(ellipse at 12% 0%,#1c67b5 0%,transparent 48%),linear-gradient(155deg,#1664bb 0%,#074b9c 55%,#052e70 100%);background-attachment:fixed}
h1,h2,h3{font-family:'Manrope',sans-serif!important;letter-spacing:-.04em;color:inherit}
.block-container{max-width:1100px;padding-top:3rem;padding-bottom:3rem}
[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"]{background:linear-gradient(170deg,#eef8ff,#dbeafa);color:var(--ink);border-right:1px solid #ffffff70}
[data-testid="stSidebar"] .block-container{padding-top:2rem}
.stApp [data-testid="stCaptionContainer"]{color:#dfedff;opacity:1}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"], [data-testid="stForm"] [data-testid="stCaptionContainer"], [data-testid="stExpander"] [data-testid="stCaptionContainer"], [data-testid="stChatMessage"] [data-testid="stCaptionContainer"]{color:var(--muted)}
.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{border-radius:24px;min-height:48px;font-weight:600;border:1px solid #d6e8f9;box-shadow:0 4px 16px #002c6a14}
.stButton>button:not([kind="primary"]),.stFormSubmitButton>button:not([kind="primary"]),.stDownloadButton>button{color:var(--ink);background:#f5faff}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:var(--blue);color:white;border-color:var(--blue)}
[data-testid="stForm"]{background:#f5fafff5;color:var(--ink);border:1px solid #ffffff99;border-radius:26px;padding:26px;box-shadow:0 14px 40px #00255520}
[data-testid="stForm"] label,[data-testid="stForm"] h3{color:var(--ink)}
.stApp [data-testid="stWidgetLabel"] p{color:#edf7ff}
.stApp [data-testid="stRadio"] [role="radiogroup"] label p{color:#edf7ff}
.stApp .st-key-navigation [data-testid="stRadio"] [role="radiogroup"] label p,.stApp [data-testid="stForm"] [data-testid="stRadio"] [role="radiogroup"] label p{color:var(--ink)}
.stApp [data-testid="stAlert"]{background:#f2f8ff;color:var(--ink)}
.stApp [data-testid="stAlert"] p{color:var(--ink)}
.stApp [data-testid="stForm"] [data-testid="stWidgetLabel"] p,.stApp [data-testid="stExpander"] [data-testid="stWidgetLabel"] p,.stApp [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{color:var(--ink)}
[data-testid="stMetric"]{padding:20px 24px;border:1px solid #ffffff80;border-radius:24px;background:#f5faffed;color:var(--ink);box-shadow:0 10px 30px #00255516}
[data-testid="stMetricValue"]{font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700}
.hero{padding:40px;border-radius:32px;background:linear-gradient(125deg,#13569b,#074381);border:1px solid #ffffff45;color:white;margin:18px 0 28px;position:relative;overflow:hidden;box-shadow:0 18px 50px #00295720}
.hero:after{content:"";position:absolute;width:440px;height:180px;right:-110px;bottom:-120px;border-radius:50%;border:1px solid #ffffff45;box-shadow:0 -18px 0 0 #ffffff09,0 -36px 0 0 #ffffff08,0 -54px 0 0 #ffffff06;pointer-events:none}
.hero h1{color:white;font-size:2.7rem;font-weight:800;max-width:650px;line-height:1.18;margin:12px 0 18px}
.hero p{color:#e4f1ff;max-width:590px;margin-bottom:5px;line-height:1.7}
.eyebrow{font-size:.76rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:#d5ecff}
.wordmark{font-family:'Manrope',sans-serif;font-size:2rem;font-weight:800;letter-spacing:-.07em;color:white}
[data-testid="stSidebar"] .wordmark{color:var(--blue)}
.kicker{font-size:.8rem;text-transform:uppercase;letter-spacing:.14em;font-weight:700;color:#d6eaff}
.exercise{padding:28px;border:1px solid #ffffffb3;border-radius:26px;background:linear-gradient(135deg,#ffffff,#e9f4ff);color:var(--ink);margin:16px 0;box-shadow:0 12px 32px #00295720}
.exercise h3{margin:14px 0 8px;color:var(--ink)}
.pill{display:inline-block;padding:6px 12px;background:#dceeff;border-radius:20px;color:#155a9e;font-size:.78rem;font-weight:700}
.day{padding:18px 8px;text-align:center;border:1px solid #ffffff40;border-radius:22px;min-height:110px;background:#ffffff12;color:#e2efff}
.week-grid{display:grid;grid-template-columns:repeat(7,minmax(85px,1fr));gap:10px;overflow-x:auto;padding-bottom:10px}
.day.active{background:#edf7ff;color:#125ba5;border-color:#ffffff;box-shadow:0 6px 20px #00295720}.day b{font-size:1.4rem;display:block;margin:6px 0}.day .muted{color:inherit}
.muted{color:var(--muted);font-size:.95rem}.proposal{padding:28px;background:#eff8ff;border:1px solid #b8ddff;border-radius:26px;margin:18px 0;color:var(--ink)}
[data-testid="stChatMessage"]{background:#f2f8fff2;color:var(--ink);border-radius:24px}
[data-testid="stExpander"]{background:#f2f8fff2;color:var(--ink);border-radius:20px}
.proposal .kicker{color:#155a9e}
.st-key-navigation{background:#e6f2fff5;border:1px solid #ffffffb3;border-radius:30px;padding:10px 16px;margin:20px 0 28px;box-shadow:0 10px 30px #00234f25;color:var(--ink)}
.st-key-navigation [role="radiogroup"]{display:flex;justify-content:space-around;gap:6px;flex-wrap:wrap}
.st-key-navigation [role="radiogroup"] label{margin:0;min-height:48px;padding:10px 12px;border-radius:24px;cursor:pointer;color:#305575}
.st-key-navigation [role="radiogroup"] label:has(input:checked){background:#c2e1ff;color:#0758aa;box-shadow:inset 0 0 0 1px #126bc5}
.st-key-navigation [role="radiogroup"] p{font-size:1rem;font-weight:700;white-space:nowrap}
:where(button,input,textarea,select,a,[role="slider"]):focus-visible,.st-key-navigation label:focus-within{outline:3px solid #12365b!important;outline-offset:3px;box-shadow:0 0 0 6px white!important}
.st-key-safety button{background:#fff1f0;color:#8c201d;border:2px solid #b93c35;font-weight:700}
.hero.compact{padding:28px 32px}.hero.compact h1{font-size:2rem;margin:10px 0}
.exercise .prescription{font-family:'Manrope',sans-serif;font-size:1.45rem;font-weight:700;color:#125ba5;margin:12px 0}
footer{visibility:hidden}
@media(max-width:600px){.block-container{padding:4rem 1rem 3rem}.hero,.hero.compact{padding:24px;border-radius:26px}.hero h1,.hero.compact h1{font-size:2rem}[data-testid="stForm"]{padding:18px}.exercise{padding:22px}.st-key-navigation{padding:8px;border-radius:24px}.st-key-navigation [role="radiogroup"]{justify-content:flex-start}.st-key-navigation [role="radiogroup"] label{padding:10px 8px}.week-grid{grid-template-columns:1fr;overflow:visible;gap:8px}.day{display:flex;align-items:center;justify-content:space-between;min-height:56px;padding:10px 18px;border-radius:16px}.day b{margin:0}.day .muted{min-width:40px;text-align:left}}
</style>''', unsafe_allow_html=True)

st.markdown('<style>' + Path(__file__).with_name('aquatic.css').read_text() + '</style>', unsafe_allow_html=True)

if 'zinc' not in st.session_state or 'activity_sessions' not in st.session_state.zinc:
    st.session_state.zinc = engine.new_state({'name': '', 'age': 52, 'level': 'beginner', 'limits': [], 'mci': False, 'clinician_clearance': False, 'toggles': {'yoga': False, 'brain': False}})
s = st.session_state.zinc

def esc(value):
    return html.escape(str(value))


def reset(profile=None):
    st.session_state.zinc = engine.new_state(profile)
    for key in list(st.session_state):
        if key != 'zinc':
            del st.session_state[key]
    st.rerun()


with st.sidebar:
    st.caption('TRY THE DEMO')
    if st.button('Load Maria', width='stretch'):
        reset(engine.MARIA)
    st.caption('Maria · 52 · beginner · knee limitations. Loading Maria resets all demo data and requires a new screen.')
    if st.button('Start fresh', width='stretch'):
        reset({'name': '', 'age': 52, 'level': 'beginner', 'limits': [], 'mci': False, 'clinician_clearance': False, 'toggles': {'yoga': False, 'brain': False}})
    st.divider()
    st.caption('General wellness, not medical advice. Fictional demo data only. Data lasts for this browser session and may reset on refresh or reconnect.')

left, right = st.columns([4, 1])
with left:
    st.markdown('<div class="brand-row"><span class="wordmark">✳ ZINC</span><span class="demo-pill">Fictional demo</span></div>', unsafe_allow_html=True)
with right:
    st.empty()
with st.container(key='safety'):
    if s['plan'] is not None and not s['stopped']:
        if st.button('■ Stop — chest pain, dizziness or faintness', type='secondary', width='stretch'):
            engine.stop(s)
            st.rerun()
if s['stopped']:
    st.error(engine.STOP_MESSAGE)
    st.info('This session is locked. Load Maria or Start fresh to reset the fictional demo. Resetting is not medical clearance.')
    st.stop()


from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import activities

LABELS = {'strength': 'Strength & balance', 'yoga': 'Yoga', 'brain': 'Brain games', 'relaxation': 'Relaxation'}
BADGES = {'strength': 'Strong / Moderate', 'yoga': 'Moderate', 'brain': 'Moderate', 'relaxation': 'Emerging'}
SOURCES = {'brain': 'ACTIVE 10-year results, J Am Geriatr Soc 2014 — trained reasoning abilities.',
           'relaxation': 'Breathwork meta-analysis, Scientific Reports 2023 — self-reported stress.'}


def rerun_to(page):
    s['requested_page'] = page
    st.rerun()


onboarding = st.empty()
if s['safety_result'] is None or s['plan'] is None:
    with onboarding.container():
        st.title('Your week starts with you.')
        step = s['onboarding_step']
        st.caption(['Step 1 of 3 · Profile', 'Step 2 of 3 · Safety screen', 'Step 3 of 3 · Focus'][step])
        st.progress((step + 1) / 3)
        if step == 0:
            with st.form('profile_step'):
                name = st.text_input('First name', s['profile']['name'], max_chars=40)
                age = st.number_input('Age', 20, 110, s['profile']['age'])
                level = st.selectbox('Fitness level', ['beginner', 'active', 'trained'], index=['beginner', 'active', 'trained'].index(s['profile']['level']))
                limits = st.multiselect('Movement limitations', ['knees', 'back', 'balance'], default=s['profile']['limits'])
                mci = st.checkbox('A clinician has identified mild cognitive impairment', s['profile'].get('mci', False))
                clearance = st.checkbox('I have clinician sign-off for supported exercise (required for age 80+ or mild cognitive impairment)', s['profile'].get('clinician_clearance', False))
                confirmed = st.checkbox('I am using fictional information for this prototype.', value=s.get('fictional_confirmed', False))
                if st.form_submit_button('Continue to safety', type='primary'):
                    s['profile'].update(name=name.strip(), age=int(age), level=level, limits=limits, mci=mci, clinician_clearance=clearance)
                    s['fictional_confirmed'] = confirmed
                    if not name.strip() or not confirmed:
                        st.error('Enter a first name and confirm fictional demo use.')
                    else:
                        s['onboarding_step'] = 1
                        st.rerun()
        elif step == 1:
            st.subheader('Before we make a plan')
            st.caption('Shortened demo questions adapted from PAR-Q+. This is not the full validated questionnaire.')
            with st.form('safety_step'):
                answers = {k: st.radio(label, ['No', 'Yes'], index=['No', 'Yes'].index(s['screening_answers'][k]) if s['screening_answers'].get(k) else None, horizontal=True) for k, label in engine.QUESTIONS.items()}
                back = st.form_submit_button('Back to profile')
                go = st.form_submit_button('Continue to focus', type='primary')
                if back or go:
                    s['screening_answers'] = answers
                    if back:
                        s['onboarding_step'] = 0
                        st.rerun()
                    elif any(v is None for v in answers.values()):
                        st.error('Answer every question before continuing.')
                    else:
                        result = engine.safety_check({k: v == 'Yes' for k, v in answers.items()})
                        if result == 'clinician':
                            st.error('Please see a clinician before starting. No plan will be generated and coaching is blocked. Seek urgent help for current severe symptoms.')
                        elif (s['profile']['age'] >= 80 or s['profile'].get('mci')) and not s['profile'].get('clinician_clearance'):
                            st.error('Clinician sign-off is required. Return to your profile after obtaining guidance.')
                        else:
                            s['safety_result'] = result
                            s['onboarding_step'] = 2
                            engine.event(s, 'screening', result=result)
                            st.rerun()
        else:
            st.subheader('Make room for what matters to you')
            st.write('Choose days that fit your routine. All four baseline sections stay included. You can add optional activities after creating your week.')
            with st.form('focus_step'):
                st.caption('Quick Sunday extras · optional')
                yoga = st.checkbox('Extra yoga', s['profile']['toggles'].get('yoga', False))
                brain = st.checkbox('Extra brain and relaxation', s['profile']['toggles'].get('brain', False))
                today = datetime.now(ZoneInfo('America/New_York')).date()
                start = st.date_input('Week beginning (Monday)', value=s.get('chosen_start', today - timedelta(days=today.weekday())))
                st.markdown('#### Choose your baseline days')
                strength_default = ['Mon', 'Wed', 'Fri'] if engine.assign_tier(s['profile']['age']) in ('Build', 'Rebuild') and not s['profile'].get('mci') else ['Mon', 'Thu']
                day_choices = {section: st.multiselect(f'{label} days', engine.WEEKDAYS, default=s.get('chosen_days', {}).get(section, strength_default if section == 'strength' else ['Tue', 'Sat']), key=f'choose_{section}_days') for section, label in LABELS.items()}
                st.caption('Keep the displayed baseline frequency. Strength needs a rest day between sessions. Optional extras can be added later.')
                back = st.form_submit_button('Back to safety')
                create = st.form_submit_button('Create my complete week', type='primary')
                if back or create:
                    s['profile']['toggles'] = {'yoga': yoga, 'brain': brain}
                    s['chosen_start'] = start
                    s['chosen_days'] = day_choices
                    if back:
                        s['onboarding_step'] = 1
                        st.rerun()
                    elif start.weekday() != 0:
                        st.error('Choose a Monday so the dated weekly schedule matches your training days.')
                    else:
                        try:
                            initial = engine.make_week(s['profile'], s['safety_result'], engine.AVAILABLE, start)
                            s['plan'] = engine.choose_days(initial, {section: [engine.WEEKDAYS.index(day) for day in days] for section, days in day_choices.items()})
                            engine.event(s, 'plan_created')
                            st.rerun()
                        except ValueError as exc:
                            st.error(str(exc))
        st.stop()
    
onboarding.empty()
if s.get('requested_page'):
    st.session_state.page = s.pop('requested_page')
with st.container(key='navigation'):
    page = st.radio('Your space', ['Overview', 'Your week', 'Train', 'Coach', 'Progress'], horizontal=True, label_visibility='collapsed', key='page', format_func=lambda value: {'Overview': ':material/home: Overview', 'Your week': ':material/calendar_month: Week', 'Train': ':material/exercise: Train', 'Coach': ':material/forum: Coach', 'Progress': ':material/monitoring: Progress'}[value])
plan = s['plan']
if plan['fall_risk']:
    st.info('Supported mode: seated and chair-supported options, with no power cue.')


def exercise_card(item):
    power = '<p class="pill">Power: lift fast, lower slow</p>' if item['power'] else ''
    st.markdown(f'<div class="exercise"><span class="evidence {esc(item["badge"].lower())}">{esc(item["badge"])} evidence</span><h3>{esc(item["name"])}</h3><p>{esc(item["version"])}</p><p class="prescription">{item["sets"]} × {item["reps"]} {esc(item["unit"])}</p><p>{esc(item["cue"])}</p>{power}<div class="variant-chips"><span>Easier: {esc(item["easier"])}</span><span>Harder: {esc(item["harder"])}</span></div></div>', unsafe_allow_html=True)
    with st.popover('Why this exercise?'):
        st.write(item['source'])
        if item['power']:
            st.write('Power cue: lift fast, lower slow within a comfortable range. Moderate evidence; prototype cue for age 40+. Alternatives are examples only; your current prescription stays unchanged.')
        else:
            st.write('Alternatives are examples only; your current prescription stays unchanged.')


def status(activity):
    return s['activity_sessions'].get(activity['id'], {}).get('status', 'not started')


def status_label(activity):
    return {'not started': 'Not started', 'partial': 'In progress', 'completed': 'Done', 'skipped': 'Skipped'}.get(status(activity), status(activity))


def show_schedule():
    for activity in plan['activities']:
        label = LABELS[activity['section']]
        with st.container(key=f"act_{activity['id']}"):
            st.subheader(f"{nice_date(activity['date'])} · {label}")
            badge = BADGES[activity['section']]
            badges = ''.join(f'<span class="evidence {esc(word.lower())}">{esc(word)}</span>' for word in badge.split(' / '))
            st.markdown(f'<div class="activity-meta"><span>{activity["minutes"]} min estimated</span><span class="status-chip">{esc(status_label(activity))}</span>{badges}</div>', unsafe_allow_html=True)
            st.caption({'strength': 'Large-muscle patterns and supported balance. Record repetitions, effort and pain after every set.', 'yoga': 'Five guided pose cards with supported alternatives and feedback.', 'brain': 'Five reasoning and pattern puzzles. Difficulty follows your answers.', 'relaxation': 'Slow breathing: five seconds in, five seconds out. Choose three or five minutes.'}[activity['section']])
            session = s['activity_sessions'].get(activity['id'])
            if st.button('Review' if session and session['finished'] else 'Resume' if session else 'Start activity', key='start_' + activity['id']):
                engine.start_activity(s, activity['id'])
                rerun_to('Train')
            st.caption('Optional extra' if activity.get('optional') else 'Baseline activity')
            if not session or not session['finished']:
                with st.expander('Reschedule or remove' if activity.get('optional') else 'Reschedule'):
                    with st.form('move_' + activity['id']):
                        selected_day = st.selectbox('Move to', engine.WEEKDAYS, index=(datetime.fromisoformat(activity['date']).date() - datetime.fromisoformat(plan['start_date']).date()).days)
                        move = st.form_submit_button('Save new day')
                        remove = st.form_submit_button('Remove optional activity') if activity.get('optional') and not session else False
                        if move or remove:
                            try:
                                engine.change_schedule(s, activity_id=activity['id'], day=engine.WEEKDAYS.index(selected_day), remove=remove)
                                st.rerun()
                            except ValueError as exc:
                                st.error(str(exc))


def submit_strength(exercise_id, keys):
    engine.log_set(s, exercise_id, int(st.session_state[keys[0]]), st.session_state[keys[1]], st.session_state[keys[2]])


def submit_yoga(keys):
    engine.log_yoga(s, st.session_state[keys[0]], st.session_state[keys[1]])


def submit_brain(key):
    answer = st.session_state[key]
    if answer is None:
        engine.active_session(s)['puzzle_feedback'] = 'Enter a whole number first.'
    else:
        correct, reason = engine.answer_puzzle(s, int(answer))
        engine.active_session(s)['puzzle_feedback'] = ('Correct. ' if correct else 'Not quite. ') + reason


if page == 'Overview':
    st.title(f"Your complete week, {s['profile']['name']}.")
    st.write(f"{plan['tier']} · Week {plan['week']} · Beginning {nice_date(plan['start_date'])}")
    st.write('Strength for everyday life, room to stretch, a reasoning challenge, and a moment to relax.')
    cards = []
    icons = {'strength': 'exercise', 'yoga': 'self_improvement', 'brain': 'psychology', 'relaxation': 'air'}
    for section, label in LABELS.items():
        scheduled = [a for a in plan['activities'] if a['section'] == section]
        complete = sum(status(a) == 'completed' for a in scheduled)
        percent = round(100 * complete / len(scheduled)) if scheduled else 0
        cards.append(f'<section class="overview-card"><span class="material-symbols-rounded" aria-hidden="true">{icons[section]}</span><h2>{esc(label)}</h2><div class="mini-ring" style="--completion:{percent}%"><span>{complete}/{len(scheduled)}</span></div><p>{complete} of {len(scheduled)} done</p></section>')
    st.markdown('<div class="overview-grid">' + ''.join(cards) + '</div>', unsafe_allow_html=True)
    today = datetime.now(ZoneInfo('America/New_York')).date().isoformat()
    remaining = [a for a in plan['activities'] if not s['activity_sessions'].get(a['id'], {}).get('finished')]
    remaining.sort(key=lambda a: (0 if status(a) == 'partial' else 1 if a['date'] == today else 2 if a['date'] > today else 3, a['date']))
    with st.container(key='next_activity'):
        st.subheader('Your next activity')
        if remaining:
            next_activity = remaining[0]
            st.write(f"{LABELS[next_activity['section']]} · {nice_date(next_activity['date'])} · {next_activity['minutes']} min estimated")
            if st.button('Resume next activity' if status(next_activity) == 'partial' else 'Start next activity', type='primary'):
                engine.start_activity(s, next_activity['id'])
                rerun_to('Train')
            st.caption('Choose Your week to move this activity to another day.')
        else:
            st.success('Every activity is finished or ended. Review your week with your coach.')
    actions = st.columns(2)
    with actions[0]:
        if st.button('Explore my week'):
            rerun_to('Your week')
    with actions[1]:
        if st.button('Ask my coach'):
            rerun_to('Coach')
    with st.container(key='next_week'):
        st.subheader('Next week')
        if s['next_plan']:
            for item in s['next_plan']['exercises']:
                current = engine.prescription(plan, item['id'])
                if item['id'] in s['next_plan']['adjusted_exercises']:
                    st.write(f"{item['name']}: {current['reps']} → {item['reps']} {item['unit']}")
        else:
            st.write('No changes yet. Your coach will suggest next week’s goal at check-in.')
        if st.button('Start next week'):
            try:
                engine.start_next_week(s)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

elif page == 'Your week':
    st.title('Your week')
    with st.popover('About activity estimates'):
        st.write('Durations are estimates, not measured exercise time. Source badges describe strength, function, trained reasoning or stress outcomes, never disease outcomes.')
    with st.expander('Add an optional activity'):
        with st.form('add_activity'):
            added_section = st.selectbox('Activity type', list(LABELS), index=3, format_func=LABELS.get)
            added_day = st.selectbox('Day', engine.WEEKDAYS, index=2)
            st.caption(f'Adding this activity will increase your week from {len(plan["activities"])} to {len(plan["activities"]) + 1} activities. Baseline completion is tracked separately from extras.')
            st.caption('At most one activity of each type per day. Strength: at most three days with a rest day between; supported mode keeps its prescribed frequency. These are prototype scheduling limits, not clinical clearance.')
            if st.form_submit_button('Add to my week', type='primary'):
                try:
                    engine.change_schedule(s, section=added_section, day=engine.WEEKDAYS.index(added_day))
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
    st.caption('Your chosen days and optional activities carry into next week. Finished activities keep their recorded dates.')
    show_schedule()
    with st.expander('Strength and balance prescriptions'):
        for item in plan['exercises']:
            exercise_card(item)
    st.button('Quick look speed game · Mockup only', disabled=True)
    st.caption('The speed game is not scored or included in progress. Reasoning games are fully playable.')

elif page == 'Train':
    st.title(LABELS[engine.active_session(s)['section']] if s['active_activity'] else 'Choose your activity')
    if not s['active_activity']:
        st.info('Choose a dated activity from Your week to begin.')
        if st.button('Choose an activity'):
            rerun_to('Your week')
    else:
        session = engine.active_session(s)
        section = session['section']
        st.subheader(f"{LABELS[section]} · {nice_date(session['date'])}")
        if session['finished']:
            st.success('Activity completed.' if session['status'] == 'completed' else f"Activity ended: {session['status']}.")
            if session.get('pain_limited') or any(f['pain'] >= 4 for f in session['feedback']):
                st.warning('Pain reached 4 or higher. Do not push through pain; seek guidance if pain persists.')
            actions = st.columns(2)
            with actions[0]:
                if st.button('Choose another activity', type='primary'):
                    rerun_to('Your week')
            with actions[1]:
                if st.button('Review with my coach'):
                    rerun_to('Coach')
        elif section == 'strength':
            item = plan['exercises'][s['cursor']]
            st.progress(s['cursor'] / len(plan['exercises']), text=f"Exercise {s['cursor'] + 1} of {len(plan['exercises'])} · Set {s['set_index'] + 1} of {item['sets']}")
            exercise_card(item)
            if session.get('pain_limited'):
                st.warning('The painful exercise was ended. Do not push through pain; stop the session if discomfort continues.')
            keys = [f"{field}_{session['id']}_{s['logs']['version']}" for field in ('count', 'effort', 'pain')]
            with st.form(f"set_{session['id']}_{s['logs']['version']}"):
                reps = st.number_input('Completed repetitions / seconds', 0, 100, item['reps'], key=keys[0])
                effort = st.slider('Effort · 1 easy, 10 maximal', 1, 10, 6, key=keys[1])
                pain = st.slider('Pain · 0 none, 10 severe', 0, 10, 0, key=keys[2])
                st.form_submit_button('Done set', type='primary', on_click=submit_strength, args=(item['id'], keys))
        elif section == 'yoga':
            pose = plan['yoga'][session['pose_index']]
            st.write(f"Pose {session['pose_index'] + 1} of 5 · {pose['name']}")
            st.subheader(pose['version'])
            st.write(pose['cue'])
            st.caption(f"{pose['badge']} evidence · {pose['source']}. Move gently for about one minute per card; rest whenever needed.")
            keys = [f"yoga_{field}_{session['id']}_{session['pose_index']}" for field in ('effort', 'pain')]
            with st.form(f"pose_{session['id']}_{session['pose_index']}"):
                effort = st.slider('Effort · 1 easy, 10 maximal', 1, 10, 3, key=keys[0])
                pain = st.slider('Pain · 0 none, 10 severe', 0, 10, 0, key=keys[1])
                st.form_submit_button('Done pose', type='primary', on_click=submit_yoga, args=(keys,))
        elif section == 'brain':
            puzzle = engine.current_puzzle(s)
            st.write(f"Puzzle {len(session['answers']) + 1} of 5 · Level {s['brain_level']} of 4")
            st.subheader(puzzle['question'])
            st.caption('Find the next number. Three consecutive correct answers raise the level; two misses lower it. This practices reasoning and is not a cognitive assessment.')
            st.caption('Moderate evidence · ' + SOURCES['brain'])
            if session.get('puzzle_feedback'):
                st.info(session['puzzle_feedback'])
            key = f"answer_{session['id']}_{len(session['answers'])}"
            with st.form(f"puzzle_{session['id']}_{len(session['answers'])}"):
                st.number_input('Next number', min_value=-100000, max_value=100000, value=None, step=1, key=key)
                st.form_submit_button('Check answer', type='primary', on_click=submit_brain, args=(key,))
        elif section == 'relaxation':
            st.caption('Emerging evidence · ' + SOURCES['relaxation'])
            st.write('Breathe comfortably. Follow the circle only if the pace feels natural. Stop if you feel unwell.')
            minutes = st.radio('Practice length', [3, 5], horizontal=True, format_func=lambda n: f'{n} minutes', key='breath_' + session['id'])
            st.markdown('<style>@keyframes breathe{0%,100%{transform:scale(.65)}50%{transform:scale(1)}}@keyframes breathword{0%,49.99%{content:"Breathe in"}50%,100%{content:"Breathe out"}}.breath-space{height:240px;display:grid;place-items:center}.breath-circle{width:180px;height:180px;border-radius:50%;background:#dceeff;color:#12365b;display:grid;place-items:center;animation:breathe 10s ease-in-out infinite}.breath-circle:after{content:"Breathe in";animation:breathword 10s steps(1) infinite}@media(prefers-reduced-motion:reduce){.breath-circle{animation:none}.breath-circle:after{animation:none;content:"In 5s · Out 5s"}}</style><div class="breath-space" aria-label="Breathe in for five seconds and out for five seconds"><div class="breath-circle"></div></div>', unsafe_allow_html=True)
            st.caption('The circle loops continuously; it is not a countdown. Completion time is self-reported.')
            if st.button('I completed my breathing practice', type='primary'):
                engine.finish_activity(s, minutes=minutes)
                st.rerun()
        if not session['finished']:
            if st.button('Skip / end this activity'):
                engine.finish_activity(s, skipped=True)
                st.rerun()
        with st.form('symptoms'):
            symptom = st.text_input('Feeling unwell? Describe symptoms', max_chars=500)
            if st.form_submit_button('Check symptoms'):
                if engine.red_flag(symptom):
                    engine.stop(s)
                    st.rerun()
                else:
                    st.info('This text check cannot assess symptoms. Press Stop whenever you feel unwell or uncertain.')

elif page == 'Coach':
    st.title('Your coach')
    st.write('Your personal coach can explain your scheduled activities, review your history and propose strength changes for next week. You decide whether to accept.')
    for message in s['messages']:
        with st.chat_message(message['role']):
            st.text(message['text'])
    checkin = st.button('Weekly check-in', type='primary')
    message = st.chat_input('Ask about strength, yoga, brain games or relaxation', max_chars=2000)
    if checkin or message:
        message = message or 'Review my complete weekly activity history and propose a strength goal for next week when feedback supports it.'
        try:
            secrets = {'GEMINI_API_KEY': st.secrets.get('GEMINI_API_KEY'), 'MODEL': st.secrets.get('MODEL')}
        except FileNotFoundError:
            secrets = {}
        s['messages'].append({'role': 'user', 'text': message})
        with st.spinner('Reviewing your week…'):
            reply = coach.coach_turn(message, s, secrets)
        s['messages'].append({'role': 'assistant', 'text': reply})
        st.rerun()
    with st.expander('Rules-only strength adjustment · no AI'):
        st.caption('Works without an API key. Log strength feedback first. Finish the current activity before accepting.')
        with st.form('rule_preview'):
            exercise_id = st.selectbox('Exercise', [i['id'] for i in plan['exercises']], format_func=lambda x: engine.prescription(plan, x)['name'])
            direction = st.selectbox('Next week', ['same', 'harder', 'easier'])
            if st.form_submit_button('Preview adjustment'):
                s['pending_change'] = None
                try:
                    s['pending_change'] = engine.progress(plan, s['logs'], exercise_id, direction)
                    engine.event(s, 'rules_preview', exercise_id=exercise_id)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
    p = s['pending_change']
    if p:
        item = engine.prescription(plan, p['exercise_id'])
        st.subheader(f"Pending for next week · {item['name']}")
        st.write(f"{p['current']} → {p['proposed']} {item['unit']} · {p['reason']}")
        unfinished = any(not a['finished'] for a in s['activity_sessions'].values() if a['week'] == plan['week'])
        actions = st.columns(2)
        with actions[0]:
            if st.button('Accept for next week', type='primary', disabled=unfinished):
                try:
                    engine.accept_pending_change(s)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        with actions[1]:
            if st.button('Decline · keep my plan'):
                engine.decline_pending_change(s)
                st.rerun()
        if unfinished:
            st.caption('Finish or end unfinished activities before accepting.')

elif page == 'Progress':
    import progress_board as board_ui
    st.title('Progress')
    plans = s['history'] + [plan]
    weeks = [p['week'] for p in plans]
    selected = st.selectbox('Week', weeks, index=len(weeks)-1,
                           format_func=lambda week: f"Week {week} · {nice_range(next(p for p in plans if p['week'] == week)['start_date'], (datetime.fromisoformat(next(p for p in plans if p['week'] == week)['start_date']) + timedelta(days=6)).date().isoformat())}")
    selected_plan = next(p for p in plans if p['week'] == selected)
    board = board_ui.summarize(selected_plan, s['activity_sessions'])
    sessions = [a for a in s['activity_sessions'].values() if a['week'] == selected]
    day_markup = ''.join(f'<div class="calendar-day"><span>{day.strftime("%a")}</span><strong>{day.day}</strong><small>{count} done</small></div>' for day,count in zip(board['days'],board['daily']))
    st.markdown(f'<div class="date-rail" aria-label="Scheduled week">{day_markup}</div>', unsafe_allow_html=True)
    section_markup = ''.join(f'<div class="section-reading"><span>{esc(section["name"])}</span><strong>{section["done"]}<small> / {section["total"]}</small></strong><span>completed</span></div>' for section in board['sections'])
    comparison = 'Your first week sets the starting point.'
    previous = next((p for p in plans if p['week'] == selected - 1), None)
    if previous:
        prior = board_ui.summarize(previous, s['activity_sessions'])
        comparison = f'Previous week: {prior["done"]} of {prior["total"]} scheduled activities completed.'
    st.markdown(f'<section class="progress-hero"><div class="completion-gauge" style="--completion:{board["percent"]}%" role="img" aria-label="{board["done"]} of {board["total"]} baseline activities completed, {board["percent"]} percent"><div><strong>{board["percent"]}<small>%</small></strong><span>baseline complete</span></div></div><div class="weekly-takeaway"><h2>Your week, taking shape.</h2><p>{board["done"]} of {board["total"]} baseline activities completed · {board["partial"]} partially completed</p><p>{comparison}</p></div></section><div class="section-readings">{section_markup}</div>', unsafe_allow_html=True)
    st.caption(f"Optional extras: {board['extra_done']} of {board['extra_total']} completed. Extras never lower your baseline completion.")
    st.markdown('<section class="chart-panel"><div class="chart-heading"><h2>Your activity rhythm</h2><span>Completed activities · scheduled day</span></div>' + board_ui.activity_chart(board) + '<p>Each point counts completed activities scheduled for that day. Partial and skipped activities are listed separately below.</p></section>', unsafe_allow_html=True)
    answers = [r for a in sessions if a['section'] == 'brain' for r in a['answers']]
    accuracy = f"{sum(r['correct'] for r in answers) / len(answers):.0%}" if answers else '—'
    minutes = sum(a.get('completed_minutes', 0) for a in sessions)
    st.markdown(f'<div class="wellness-readings"><section><h2>Reasoning practice</h2><strong>{accuracy}</strong><p>Reasoning accuracy: {accuracy if answers else "no answers yet"} · {len(answers)} answers</p></section><section><h2>Time to unwind</h2><strong>{minutes}<small> min</small></strong><p>Relaxation: {minutes} self-reported minutes</p></section></div>', unsafe_allow_html=True)
    if selected == plan['week']:
        st.write(f"Current reasoning level: {s['brain_level']} / 4")
    elif answers:
        st.write(f"Last recorded reasoning level: {answers[-1].get('level_after', answers[-1]['level'])} / 4")
    else:
        st.write('Reasoning level: no answers this week')
    if board['done'] < board['total'] and selected == plan['week']:
        st.button('Choose an activity →', type='primary', on_click=lambda: s.update(requested_page='Your week'))
    st.subheader('Activity board')
    with st.expander('View dated activities and status'):
        st.dataframe(friendly_rows(board['rows']), hide_index=True, width='stretch')
    with st.expander('Pain and effort · recorded feedback'):
        feedback = board_ui.feedback_rows(s, selected_plan)
        if feedback:
            st.caption('Self-reported pain: 0–10. Effort: 1–10. Each observation belongs to the movement and activity shown; unlike activities are not joined into a trend.')
            st.dataframe(friendly_rows(feedback), hide_index=True, width='stretch')
        else:
            st.info('Strength and yoga feedback will appear after your first recorded set or pose.')
    with st.expander('Accepted next-week adjustments'):
        accepted = [e for e in s['events'] if e['event'] == 'accepted' and e.get('week') == selected]
        if accepted:
            st.dataframe([{'Exercise': engine.prescription(selected_plan, e['exercise_id'])['name'], 'Current count': engine.prescription(selected_plan, e['exercise_id'])['reps'], 'Next-week count': e['proposed'], 'Unit': engine.prescription(selected_plan, e['exercise_id'])['unit']} for e in accepted], hide_index=True)
        else:
            st.write('No accepted adjustments this week.')
    with st.expander('Prototype diagnostics · selected week'):
        st.write('Technical event records are included in the history download.')
    st.download_button('Export all demo history', __import__('json').dumps({'profile': s['profile'], 'plan': plan, 'next_plan': s['next_plan'], 'history': s['history'], 'activity_sessions': s['activity_sessions'], 'logs': s['logs'], 'events': s['events']}, indent=2), file_name='zinc-history.json', mime='application/json')

st.divider()
st.caption('General wellness, not medical advice')
with st.popover('About ZINC'):
    st.write('Fictional demo data only. Session history may reset on refresh or reconnect. Prototype content requires professional review before real use.')
