"""Pull every season of the league from ESPN and save it to data/espn-raw.json.

Runs in GitHub Actions every Tuesday (see .github/workflows/sync-espn.yml).
Needs two repository secrets for a private league: ESPN_S2 and ESPN_SWID.
The website turns this file into standings, matchups and head-to-head records.
"""
import datetime, json, os, sys, urllib.error, urllib.request

LEAGUE_ID = 1650788944
FIRST_SEASON = 2023
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'espn-raw.json')
URL = ('https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{y}/segments/0/leagues/{id}'
       '?view=mTeam&view=mMatchupScore&view=mSettings&view=mStatus')

s2 = os.environ.get('ESPN_S2', '').strip()
swid = os.environ.get('ESPN_SWID', '').strip()
headers = {'User-Agent': 'Mozilla/5.0 (raleigh-ffl site sync)', 'Accept': 'application/json'}
if s2 and swid:
    headers['Cookie'] = f'espn_s2={s2}; SWID={swid}'


def trim(L):
    """Keep only what the site uses, so the file stays small."""
    return {
        'seasonId': L.get('seasonId'),
        'settings': {'scheduleSettings': {'matchupPeriodCount': (L.get('settings') or {}).get('scheduleSettings', {}).get('matchupPeriodCount')}},
        'status': {'currentMatchupPeriod': (L.get('status') or {}).get('currentMatchupPeriod')},
        'teams': [{k: t.get(k) for k in ('id', 'name', 'location', 'nickname', 'owners', 'primaryOwner')} for t in L.get('teams', [])],
        'members': [{k: m.get(k) for k in ('id', 'firstName', 'lastName')} for m in L.get('members', [])],
        'schedule': [{
            'matchupPeriodId': g.get('matchupPeriodId'),
            'playoffTierType': g.get('playoffTierType'),
            'winner': g.get('winner'),
            'home': {k: (g.get('home') or {}).get(k) for k in ('teamId', 'totalPoints')},
            'away': {k: (g.get('away') or {}).get(k) for k in ('teamId', 'totalPoints')} if g.get('away') else None,
        } for g in L.get('schedule', [])],
    }


today = datetime.date.today()
current = today.year if today.month >= 8 else today.year - 1
out, problems = {}, []
for y in range(FIRST_SEASON, current + 1):
    req = urllib.request.Request(URL.format(y=y, id=LEAGUE_ID), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            L = json.load(r)
        if isinstance(L, list):
            L = L[0]
        if not L.get('schedule'):
            problems.append(f'{y}: no schedule returned')
            continue
        out[str(y)] = trim(L)
        print(f'{y}: {len(L["schedule"])} games')
    except urllib.error.HTTPError as e:
        problems.append(f'{y}: HTTP {e.code}')

if problems:
    print('Problems:', '; '.join(problems))
if str(current) not in out:
    print('\nCould not read the current season. If this says HTTP 401, the ESPN cookies are missing or expired:\n'
          'update the ESPN_S2 and ESPN_SWID secrets (see README). Keeping the existing data.')
    sys.exit(1)

out['_syncedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
with open(OUT, 'w') as f:
    json.dump(out, f, separators=(',', ':'))
print('Saved', os.path.normpath(OUT))
