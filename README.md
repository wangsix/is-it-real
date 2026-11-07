# Team ratings site

The web pages for the `nba-stabilization` ratings.  This folder does not import the
Python package: the only interface is `data/ratings.json`, written by
`nba-stab export`.  It is ready to move to its own repository
(`git subtree split --prefix site`).

| file | what it is |
|---|---|
| `index.html` | the rank page (By stat, By team, Table).  Loads `data/ratings.json` |
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

## Before a public launch

- Data rights: the box scores come from Basketball-Reference.  Get Sports
  Reference's permission for a public site built on this data.  Credit the sources.
- No NBA or team logos without a licence from NBA Properties; use team
  abbreviations.  State that the site is not affiliated with the NBA.
