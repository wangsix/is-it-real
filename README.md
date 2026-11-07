# Is it real? (team ratings site)

The web pages for the `nba-stabilization` ratings.  This folder does not import the
Python package: the only interface is `data/ratings.json`, written by
`nba-stab export`.

Planned home: repository `wangsix/is-it-real`, served by GitHub Pages at
<https://wangsix.github.io/is-it-real/> (static files, no server).

| file | what it is |
|---|---|
| `index.html` | the rank page (By stat, Funnel, By team, Table).  Loads `data/ratings.json` |
| `explainer.html` | static walk-through of the method (numbers are written in by hand) |
| `build.py` | makes one self-contained file with the data inlined (stdlib only) |
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

## Data contract (`schema_version` 1)

Top level: `schema_version`, `season`, `last` (season labels), `games` ([min, max]
games played), `through` (date of the last game), `teams`, `k_seasons`,
`has_cont`, `has_full`, `stats`.

Each entry of `stats`: `name`, `unit` (`pct` or `pts`), `k`, `noise_sd`, `true_sd`,
`league_mean`, `league_mean_last`, `lower_is_better`, `style`, `q_ratio`, `beta`,
`priors` (`name`, `k`, `note`, `weight`) and `rows`.

Each row: `team`, `g`, `raw`, `raw_sd`, `raw_rk`, `last`, `delta`, `z`, `cont`,
`K_cont`, `missing`, and for each prior `P`: `P`, `P sd`, `P w`, `P rk`,
`P form`, `P form sd`, `P full`, `P full sd`.  A missing or non-finite number is
`null`.

Change `SCHEMA_VERSION` in `nba_stabilization/export.py` and `SCHEMA` in
`index.html` together when a key is removed or changes meaning.  The page shows an
error, not wrong numbers, when the versions differ.

## Publish

1. Move the folder with its history: `git subtree split --prefix site -b site-only`,
   then push branch `site-only` to `main` of `wangsix/is-it-real`.
2. In that repository: Settings → Pages → deploy from branch `main`, folder `/`.
3. Each day: `nba-stab update --out <is-it-real>/data/ratings.json`, then commit and
   push only that file.  The scraped CSVs stay on the local machine.  (Here,
   `site/data/` is ignored by the root `.gitignore`; the new repository has no such
   rule, so it tracks `data/ratings.json`.)

## Roadmap

Done: **Funnel** view.  Each team's raw value against games played (√ scale), with
95% and 99.8% noise bands (league average ± z·σ_e/√n) and a count of teams outside
the bands against the count that chance gives.  It uses the current data contract.

Next, in this order:

1. **Fan chart per team** (By team view).  The raw season-to-date value, the
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

- **Schedule (opponent) adjustment.**  Even the oracle adjustment, with the
  opponents' full-season strength, does not improve prediction in 2016–2025.
- **Luck-adjusted ratings** (opponents' 3PT% and FT% set to the league average).
  They predict the rest of the season worse than the raw ratings at all N.

## Before a public launch

- Data rights: the box scores come from Basketball-Reference.  Get Sports
  Reference's permission for a public site built on this data.  Credit the sources.
- No NBA or team logos without a licence from NBA Properties; use team
  abbreviations.  State that the site is not affiliated with the NBA.
