"""List the weekly power-rankings graphics in rankings/ for the website.

Name each image with its week, for example `2026-week-07.png` or just `week 7.jpg`
(a file without a year counts toward the current season). Uploading a second image
for the same week replaces the first one on the site.
"""
import datetime, json, os, re

ROOT = os.path.join(os.path.dirname(__file__), '..')
DIR = os.path.join(ROOT, 'rankings')
today = datetime.date.today()
current = today.year if today.month >= 8 else today.year - 1

by_week = {}
for f in sorted(os.listdir(DIR)):
    if not re.search(r'\.(png|jpe?g|webp|gif)$', f, re.I):
        continue
    stem = os.path.splitext(f)[0]
    ym = re.search(r'(20\d\d)', stem)
    year = int(ym.group(1)) if ym else current
    rest = stem.replace(ym.group(1), ' ') if ym else stem
    wm = re.search(r'(?:wk|week)\D*(\d{1,2})', rest, re.I) or re.search(r'(\d{1,2})', rest)
    if not wm:
        print('Skipped (no week number in the name):', f)
        continue
    week = int(wm.group(1))
    key = f'{year}-w{week:02d}'
    mtime = os.path.getmtime(os.path.join(DIR, f))
    if key not in by_week or mtime >= by_week[key]['_m']:
        by_week[key] = {'id': key, 'year': year, 'week': week, 'title': f'Week {week} Power Rankings',
                        'file': 'rankings/' + f, '_m': mtime}

items = sorted(by_week.values(), key=lambda r: r['id'])
for r in items:
    r.pop('_m')
with open(os.path.join(ROOT, 'data', 'rankings.json'), 'w') as fh:
    json.dump(items, fh, indent=1)
print('Rankings:', ', '.join(r['id'] for r in items) or 'none')
