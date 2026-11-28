# Is it real? (team ratings site)

The web pages for the `nba-stabilization` ratings.  This folder does not import the
Python package: the only interface is `data/ratings.json`, written by
`nba-stab export`.

Live at <https://wangsix.github.io/is-it-real/>: repository `wangsix/is-it-real`,
served by GitHub Pages (static files, no server).

| file | what it is |
|---|---|
| `index.html` | the rank page: tabs Today, Teams, Players and Lab (By stat, Funnel, Table).  Loads `data/ratings.json`.  Addresses `#today`, `#teams`, `#players`, `#lab`, `#bystat`, `#funnel`, `#table` (the older `#overview` and `#byteam` still work).  Deep links: `#teams/MIN` (a team's page), `#players/MIN` (a team's players), `#players/<name>` (name search), `#bystat/Net%20Rtg` (a stat; also `#funnel/…`, `#table/…`).  The address bar follows the team, filter or stat on screen |
| `explainer.html` | static walk-through of the method, English and 繁體中文 (EN/中文 switch; `?lang=zh` or the rank page's saved choice picks the start language).  A back link and a contents list (a fixed column on wide screens).  Each section opens with a plain summary, then the formal text.  Numbers are written in by hand |
| `build.py` | makes one self-contained file with the data inlined (stdlib only) |
| `og.png`, `og.svg` | the link-preview picture (1200 × 630) and its source |
| `data/ratings.json` | generated; not in git |
| `dist/` | generated; not in git |

## Build

```bash
uv run nba-stab update            # new games, then site/data/ratings.json
uv run nba-stab export            # only the JSON, from the stored box scores
python3 -m http.server --directory site     # http://localhost:8000 (the page fetches the JSON)
python3 site/build.py             # site/dist/rank.html, one file (for the claude.ai artifact)
```

Opening `index.html` from disk (`file://`) cannot fetch the JSON; use the server or
the single-file build.

## Sharing

- **Share as image** (Today): a dialog with a PNG drawn in the browser on a canvas, in the
  page's current theme and language: every team (1080 × 1350) or the chosen team's card
  (1200 × 675).  Buttons: the system share sheet where the browser can share files (phones),
  Download, and Copy.  Nothing is uploaded.
- **Link preview**: `index.html` and `explainer.html` carry Open Graph and Twitter card tags
  that point at `og.png` by its absolute address on the live site.  The picture has no data
  in it, so it does not go stale.  To change it, edit `og.svg` and render it again:

  ```bash
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --window-size=1200,630 --force-device-scale-factor=1 --virtual-time-budget=8000 --screenshot=site/og.png "file://$PWD/site/og.svg"
  ```

  Social sites cache the picture for days; a new one shows up late.

## Data contract (`schema_version` 1)

Top level: `schema_version`, `season`, `last` (season labels), `games` ([min, max]
games played), `through` (date of the last game), `teams`, `k_seasons`,
`has_cont`, `has_full`, `stats`, and optionally `players`.

Each entry of `stats`: `name`, `unit` (`pct` or `pts`), `k`, `noise_sd`, `true_sd`,
`league_mean`, `league_mean_last`, `league_mean_full` (league average at full
strength, or null), `lower_is_better`, `style`, `q_ratio`, `beta`, `priors`
(`name`, `k`, `note`, `note_zh` (Traditional Chinese), `weight`) and `rows`.

Each row: `team`, `g`, `raw`, `raw_sd`, `raw_rk`, `last`, `delta`, `z`, `cont`,
`K_cont`, `missing`, and for each prior `P`: `P`, `P sd`, `P w`, `P rk`,
`P form`, `P form sd`, `P full`, `P full sd`, `P mean` (the prior's own value, i.e. the
pre-season expectation; the season estimate is `P w`·`raw` + (1 − `P w`)·`P mean`).  A stat
with `opp_adjusted` (Net Rtg, Pace) also has `P opp`, `P form opp`, `P full opp`: the part of
`P`, `P form`, `P full` that comes from the opponents' level, already included in them
(so for that stat the season estimate is the formula above plus `P opp`).  A missing
or non-finite number is `null`.

`players` (missing when the player files are not there; the page then hides the Players
tab): `through`, `fit_seasons` ([first, last] season the model is fitted on), `cols` and
`stats`.  Each entry of `players.stats`: `name`, `unit` (the opportunity n is counted in:
`games`, `min`, `FGA`, …), `k` (in that unit), `r` (season-to-season correlation of the true
level), `true_sd`, `drift_sd`, `shift` (league-wide change, already taken out of every `ch`)
and `rows`.  A row is a list in the order of `cols`: `id`, `player`, `team`, `age`, `last`,
`now` (last season, this season so far), `n` (this season's opportunities), `z`, `est`, `sd`
(expected level for the rest of the season ± SD), `ch`, `ch_sd` (true change from last
season ± SD) and `p` (probability that the direction of `ch` is right, rounded down to 4
decimals).  Values are in display units (per 36 minutes, percent); rows are sorted by `p`,
highest first.

Change `SCHEMA_VERSION` in `nba_stabilization/export.py` and `SCHEMA` in
`index.html` together when a key is removed or changes meaning.  The page shows an
error, not wrong numbers, when the versions differ.

## Publish

The public repository `wangsix/is-it-real` is this folder with its history
(`git subtree split --prefix site`) plus `data/ratings.json`; GitHub Pages deploys
branch `main`, folder `/`.  Local clone: `~/Repos/is-it-real`.

1. Page changes: commit them here, then
   `git subtree split --prefix site -b site-only` and, in the clone,
   `git pull --no-rebase --no-edit <path to this repository> site-only` and push.
2. Data, each day: the `Daily update` GitHub Actions workflow of `nba_stabilization`
   commits `data/ratings.json` here (see "Daily update" in its README).  By hand:
   `uv run nba-stab update`, copy `site/data/ratings.json` to the clone's
   `data/ratings.json`, then commit and push only that file.  The scraped CSVs never
   go into this repository.
3. `.nojekyll` makes Pages serve the files as they are.  (Here,
   `site/data/` is ignored by the root `.gitignore`; the new repository has no such
   rule, so it tracks `data/ratings.json`.)

## Roadmap

Done: **Today** view (was Overview), the default for a first visit.  Written from the data on
every load, so it follows each `nba-stab update` with no extra step.  It always uses Current form
with the Continuity prior and Net Rtg.  The headline gives the answer: before game 5 "too early to
tell"; to game 40 the surprise with the largest (guess − expected)/SD on each side whose start
"looks real" (≥ 1), e.g. "12 games in: MIN's hot start and CHO's cold one look real"; from game 41
the same as "really is better / worse than expected".  Then one chart with every team (expected,
this season, best guess and 68% range, ▲▼ on the starts that look real), up to three hot and
three cold surprise cards (|raw − expected| ≥ one sampling SD, largest first), a card for a
chosen team, a signal meter n/(n+k) for seven stats at the median games played (shown as
skill % · luck %), and a Players count.  Each card gives the expected value (`P mean`), the
start, the best guess with its 68% range, the share of the gap the guess keeps ((guess −
expected)/gap, opponent term included, so the sentence adds up), and a label from (guess −
expected)/SD: ≥ 2 "clearly real", ≥ 1 "likely real", otherwise "too early to tell".  The same
three words (clearly, likely, too early / can't tell yet) are used on the team pages and the
Players view.  Checked on 2025-26 as of games 10, 20 and
41: 17 of the 18 surprise cards moved past the expectation over the rest of the season in the
direction the card said (the continuity fit includes that season, so this is not a clean
back-test).

Done: **Funnel** view.  Each team's raw value against games played (√ scale), with
95% and 99.8% noise bands (league average ± z·σ_e/√n) and a count of teams outside
the bands against the count that chance gives.  It uses the current data contract.

Done: **Players** view.  Which player changes from last season are real: one row per
player and stat with last season, this season so far, the estimate with its 68% and 95%
range, Δ ± SD and p; filters by stat, team and name, and a count on the Today page.  Uses the
`players` block.

Next, in this order:

1. **Fan chart per team** (team page).  The raw season-to-date value, the
   estimate and its ±1 SD band against game number, with the prior as a dashed line.
   Needs the estimate after each game in `ratings.json` (new keys: schema stays 1).
2. **Bump chart.**  Each team's rank by estimated Net Rtg after each game.  Uses the
   per-game estimates of item 1; useful from about game 20.
3. **Calibration page.**  How well the estimates at games 10, 20 and 41 predicted
   the rest of past seasons, and the coverage of the 68% / 95% ranges.  Most of the
   back-test code exists.  Do before the public launch.
4. **Rest-of-season projection and seeding odds.**  Simulate the remaining schedule
   from the estimates and their uncertainty: expected wins with a range, a 30 × seed
   probability heatmap, remaining strength of schedule.  Needs the remaining schedule
   (`br_games.csv` has played games only), a win-probability model, and the
   conference, play-in and tie-break rules.  Useful from about game 20.

Tested and dropped (see the main README):

- **Home/away term.**  No measurable gain in 2016–2025.  (The opponent term is on
  the page for Net Rtg, 1 to 2 % lower squared error, and for Pace, 3 to 6 %.  The older oracle adjustment at
  full weight showed no gain.)
- **Luck-adjusted ratings** (opponents' 3PT% and FT% set to the league average).
  They predict the rest of the season worse than the raw ratings at all N.

## Before a public launch

- Data rights: the box scores come from Basketball-Reference.  Get Sports
  Reference's permission for a public site built on this data.  Credit the sources.
- No NBA or team logos without a licence from NBA Properties; use team
  abbreviations.  State that the site is not affiliated with the NBA.
