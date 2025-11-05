## Purpose
This file gives short, actionable guidance for AI coding agents working on the raspi-weathercam repo.

Keep suggestions focused on the repository conventions (camera loop, config model, small Flask UI, and scheduled scripts).

## Big-picture architecture
- camloop.py: long-running PiCamera capture loop. Reads configuration on every outer loop via `config.reread()` and writes JPEGs to the configured `ImageStorePath`.
- flask/: contains a simple Flask web UI (`appWebServer.py`) that reads an SQLite DB (PathToDatabase in config.ini) and serves charts under `flask/static/`.
- config.py + config.ini: central configuration. A private user file path may be loaded (PathToUserAuthConfig). Prefer using `config.get(...)`, `getint()` etc.
- sendTemperature.py, thermometer.py and related scripts: gather DHT sensor data and push to the DB or remote services.
- crontab.txt / arch.py / viewerstat.sh: scheduling and maintenance scripts used on the Pi.

Data flows: camloop.py -> saves images (IMG-YYYYMMDD-HHMMSS.jpg) to ImageStorePath -> optional FTP upload (upload section in config.ini). DHT sensor scripts write to SQLite DB used by Flask and plotting scripts.

## Key files to inspect before changing behavior
- `camloop.py` — image capture logic, exposure handling and ftp_upload(). If changing capture timing or resolution, update config.ini keys (SecondsBetweenShots, Resolution, CropImage, BoxSizeX/BoxSizeY).
- `config.py` — single place for reading config; tests and code should call `config.reread()` where dynamic re-read is expected.
- `flask/appWebServer.py` — small UI that depends on `plot_stat.py` and a sqlite DB; static images are written to `flask/static/`.
- `README.md`, `INSTALL.md`, `install.txt` — installation hints; `INSTALL.md` points to `install.txt` for more detail.
- `userauth.ini-TEMPLATE` — template for secrets (FTP credentials, etc.). The actual path can be set with `PathToUserAuthConfig` in `config.ini`.

## Project-specific conventions and patterns
- Config is read via `config.get(...)` helpers; prefer using these functions rather than re-parsing files directly.
- camloop uses `weathercam.log` (logging.basicConfig) — keep logging calls compatible with that file-based setup.
- Image cropping/resizing settings live in `config.ini` and are applied by `crop_image()` in `camloop.py`.
- Avoid changing the filename pattern: `IMG-YYYYMMDD-HHMMSS.jpg` (used by downstream tools and uploads).

## Run and debug hints (for maintainers / agents)
- To iterate on camera logic locally, run `python camloop.py` on a machine with PiCamera or in an environment that mocks `picamera`.
- To run the web UI: from `flask/` run the included `startServer.sh` or `python appWebServer.py` (it binds to 0.0.0.0:80 by default in production use — for local debugging change port and host).
- Cron is used on the Pi. See `crontab.txt` for examples. `@reboot` runs `camloop.py` in the upstream deployment.

## Integration points & sensitive data
- FTP upload: `camloop.ftp_upload()` uses `upload` section (FtpAddress, User, Pwd). Keep credentials out of version control — use `userauth.ini` referenced by `PathToUserAuthConfig`.
- Database: SQLite path configured by `app.PathToDatabase` in `config.ini`.

## Small examples for agents
- If you add a new configurable option used by `camloop.py`, add it to `config.ini` and read it via `config.getint()` or `config.getboolean()` and call `config.reread()` if it must be dynamic.
- When modifying image processing, preserve `crop_image()` semantics (BoxPositionX/Y, BoxSizeX/Y) because these are user-configurable values.

## What NOT to change without explicit verification
- Don't change the global config loading shape in `config.py` — many scripts rely on the `get/getint/getboolean` helpers and on `PathToUserAuthConfig` behavior.
- Avoid renaming image filename pattern or storage layout without updating FTP upload and external scripts (crontab / arch.py / viewerstat.sh).

## Where to look for missing details
- `install.txt` referenced from `INSTALL.md` contains installation notes.
- Check `userauth.ini-TEMPLATE` for how secrets are expected to be provided.

If anything here is unclear or you want more examples (for tests, CI, or a more detailed runbook), tell me which area to expand.
