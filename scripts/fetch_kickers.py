"""One-off: save every starting kicker's stats for each 2026 game, plus the league's
scoring settings, to data/kickers-2026.json. Used to re-score games under the old
kicker rule (3 / 4 / 5 points by distance)."""
import json, os, urllib.request

LEAGUE_ID, YEAR = 1650788944, 2026
BASE = f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{YEAR}/segments/0/leagues/{LEAGUE_ID}'
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'kickers-2026.json')
headers = {'User-Agent': 'Mozilla/5.0 (raleigh-ffl)', 'Accept': 'application/json',
           'Cookie': f"espn_s2={os.environ['ESPN_S2'].strip()}; SWID={os.environ['ESPN_SWID'].strip()}"}


def get(query, extra=None):
    req = urllib.request.Request(BASE + query, headers={**headers, **(extra or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


base = get('?view=mSettings&view=mStatus&view=mMatchupScore')
items = base['settings']['scoringSettings']['scoringItems']
reg = base['settings']['scheduleSettings']['matchupPeriodCount']
done_weeks = sorted({g['matchupPeriodId'] for g in base['schedule']
                     if g.get('winner') not in (None, 'UNDECIDED') and g['matchupPeriodId'] <= reg})

out = {'scoringItems': items, 'weeks': {}}
for w in done_weeks:
    filt = json.dumps({'schedule': {'filterMatchupPeriodIds': {'value': [w]}}})
    data = get(f'?view=mMatchupScore&view=mScoreboard&scoringPeriodId={w}', {'x-fantasy-filter': filt})
    games = []
    for g in data.get('schedule', []):
        if g.get('matchupPeriodId') != w:
            continue
        sides = []
        for side in ('home', 'away'):
            t = g.get(side)
            if not t:
                continue
            ks = []
            for e in (t.get('rosterForCurrentScoringPeriod') or {}).get('entries', []):
                p = e.get('playerPoolEntry', {}).get('player', {})
                if p.get('defaultPositionId') != 5 and e.get('lineupSlotId') != 17:
                    continue
                st = next((s for s in p.get('stats', []) if s.get('scoringPeriodId') == w and s.get('statSourceId') == 0), {})
                ks.append({'name': p.get('fullName'), 'slot': e.get('lineupSlotId'),
                           'points': e.get('playerPoolEntry', {}).get('appliedStatTotal'),
                           'stats': st.get('stats', {}), 'applied': st.get('appliedStats', {})})
            sides.append({'teamId': t.get('teamId'), 'total': t.get('totalPoints'), 'kickers': ks})
        games.append({'winner': g.get('winner'), 'sides': sides})
    out['weeks'][str(w)] = games
    print(f'Week {w}: {len(games)} games')

with open(OUT, 'w') as f:
    json.dump(out, f, indent=1)
print('Saved', OUT)
