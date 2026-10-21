# Raleigh Fantasy Football League

The league site: standings, this week's matchups, power rankings, survivor, history and head-to-head.

## Every week

**Scores, records and matchups update on their own** every Tuesday and Wednesday morning, pulled from ESPN.

**To post power rankings:**
1. Go to the `rankings` folder in this repo.
2. Click **Add file → Upload files** and drop in the graphic.
3. Name it with the week, for example `2026-week-07.png` (just `week 7.png` works too).
4. Click **Commit changes**. The site shows it within a couple of minutes.

To fix a week's graphic, delete the old file and upload the new one.

## One-time setup

### 1. Turn on the site
Settings → **Pages** → Source: **Deploy from a branch** → Branch: **main**, folder **/ (root)** → Save.
The site goes live at https://kevinfitz95.github.io/raleigh-ffl/ in a minute or two.

### 2. Give the weekly sync your ESPN login cookies
The league is private, so ESPN needs two cookies from your browser.

1. In Chrome, open fantasy.espn.com while signed in.
2. Open DevTools (Cmd+Option+I) → **Application** tab → **Cookies** → `https://fantasy.espn.com`.
3. Copy the **Value** of `espn_s2` (long) and `SWID` (with the curly braces).
4. In this repo: Settings → **Secrets and variables → Actions → New repository secret**.
   Add `ESPN_S2` with the espn_s2 value, then `ESPN_SWID` with the SWID value.
5. Actions tab → **Sync scores from ESPN** → **Run workflow** to test it.

Secrets stay hidden even though this repo is public. ESPN expires the cookies occasionally;
if a Tuesday sync fails, GitHub emails you. Repeat steps 1 to 4 with fresh values.

## Files
- `index.html`: the site
- `data/sheet.json`: history from the commissioner sheet (champions, sticker, survivor, payouts)
- `data/espn-raw.json`: written by the weekly sync (`scripts/sync_espn.py`)
- `data/espn.json`: the first manual import, used until the first sync runs
- `data/rankings.json`: list of ranking graphics (`scripts/build_rankings.py`, runs automatically)
