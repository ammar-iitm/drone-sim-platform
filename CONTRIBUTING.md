# Contributing to AEGIS // Drone Threat Trainer

Thanks for helping. This is a training simulator for SIH problem statement 26247 (Drone Defence). Contributions that make it more realistic, more accessible or easier for instructors to use are welcome. Please read this page before opening a pull request.

## Ground rules

- **Training aid, not a weapons simulator.** Responses stay abstract, with configurable effectiveness. Don't add real weapon, ballistic or countermeasure modelling.
- **Public sources only.** Rubric rules and scenario content must come from unclassified, public material. Cite the source in [`docs/RUBRIC_SOURCES.md`](docs/RUBRIC_SOURCES.md).
- **No official branding.** Don't add the Indian Army, Government of India or any other official emblems, logos or insignia, and don't present the app as an official system. Demo data stays fictional (callsigns such as `VIPER-3`, units such as `1 TRG BN`).
- **No real personal data** in the repo, demo data or screenshots. Trainees are identified by callsign and unit only.
- **No secrets.** Never commit `.env` files, database URLs, passwords or tokens. `.gitignore` covers `.env*` and `.vercel`.
- **Offline first.** Everything must work with no internet after the first install. Bundle libraries in `app/static/vendor/` (with their licences). No CDNs, web fonts or external requests; the browser tests block them and will fail.

## Set up

You need Python 3.10 or newer and Google Chrome (the browser tests drive it).

```bash
git clone https://github.com/ammar-iitm/drone-sim-platform.git
cd drone-sim-platform
./start.sh --demo                                   # creates .venv, seeds a demo cohort, opens the app
.venv/bin/pip install -r requirements-dev.txt       # pytest and Playwright, for the tests
```

On Windows, use `start.bat --demo` and `.venv\Scripts\pip`.

## Making a change

1. **Open an issue first** for anything bigger than a small fix, so the approach can be agreed.
2. **Branch from `master`**, with a short descriptive name such as `fix-radar-dropout` or `hindi-help-page`.
3. **Match the surrounding code:** naming, comment density and idiom. Keep changes focused; don't reformat files you aren't changing.
4. **Add or update tests** for what you change. Scoring changes need a test for every new branch of the decision tree (`tests/test_scoring.py`).
5. **Run the full suite** and make sure it all passes:

   ```bash
   .venv/bin/python -m pytest
   ```

   Database changes must also pass on Postgres. Point `TEST_DATABASE_URL` at a throwaway database, never a live one:

   ```bash
   TEST_DATABASE_URL=<postgres url> .venv/bin/python -m pytest tests --ignore=tests/e2e
   ```

6. **Update the README** if behaviour, setup or a decision changes.
7. **Open a pull request** that says what changed, why, and how you tested it. Add screenshots for UI changes.

## Commit messages

- A short summary line in the imperative ("Add dawn lighting for scripted scenarios"), then a blank line and a few bullet points if needed.
- Plain text, with no tool attribution or co-author trailers for tools.

## Specific areas

- **Scoring rubric:** all numbers live in [`rubric.json`](rubric.json), which instructors edit by hand. Make small, targeted edits that keep its formatting. Bump `version` when the scoring meaning changes, and record the decision in the README.
- **Scenarios:** scripted scenarios are in `app/scenarios/*.json`, with waypoints as bearing, range and altitude. Each needs a clear learning objective and a browser test in `tests/e2e/test_scenarios.py` that checks the objective, in both the standard and the varied run. Don't change `TIMES_OF_DAY` in `app/scenario.py`: that would change every procedural seed.
- **Hindi translation:** strings are in [`app/static/js/i18n-hi.js`](app/static/js/i18n-hi.js), keyed by the exact English text. Reviews by Hindi-speaking instructors, especially of military terms, are very welcome. Translate whole sentences, not fragments.
- **Accessibility:** keep WCAG 2.1 AA contrast, keyboard access to everything, text of at least 14 px for data (12 px only for captions), and threat state shown by shape and text as well as colour. `tests/e2e/test_access.py` checks text sizes, keyboard-only play and the skip link; check contrast by hand when you change colours.
- **Database:** don't commit `data/trainer.db`; it's created on first run. Regenerate demo data with `scripts/seed_demo.py --reset`. Queries use `?` placeholders and must run on both SQLite and Postgres (see `app/db.py`).
- **Hosted version:** deploying to Vercel is done by the maintainer (`npx vercel deploy --prod`); pushing to GitHub does not deploy.

## Reporting bugs and security issues

- **Bugs:** open a GitHub issue with steps to reproduce, what you expected, what happened, and your browser and OS.
- **Security issues:** don't open a public issue. Contact the maintainer, Ammar Hashmi, through GitHub.

## Licence

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE). The bundled Three.js and Chart.js keep their own licences in `app/static/vendor/`.
