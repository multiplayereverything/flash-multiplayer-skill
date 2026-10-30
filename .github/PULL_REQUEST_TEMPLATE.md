## What this PR adds

- [ ] Directory entry (new or corrected) in `data/games.json`, with `DIRECTORY.md` re-rendered
- [ ] Game write-up in `games/<game>.md`
- [ ] New traps in `references/traps.md`
- [ ] New key map (also sent to Ruffle Together: link the PR there)
- [ ] Tool or template change (with a check in `tools/test_all.py`)
- [ ] Skill text (`skills/`, `SKILL.md`, `AGENTS.md`, `README.md`)

## Evidence

- QA level: none / lab-2p / lab-3p+ / played-online
- Which [flash-lab](skills/flash-lab/SKILL.md) steps ran, with what result (for example "0-9 passed with 2 players, twice identical"):
- Sources for every claim (links):

## Checklist

- [ ] `python -I tools/test_all.py` prints `ALL OK`
- [ ] `python tools/check_public.py` prints `0 problem(s)`
- [ ] `DIRECTORY.md` was re-rendered with `python tools/directory.py render`
- [ ] No game files, SWFs, saves or decompiled game code
- [ ] No personal info (real names, emails, local paths with usernames, tokens, private invite links)
- [ ] If an agent wrote this: the owner reviewed the diff before submitting
