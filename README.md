# AD Project

AD Project is a cross-platform terminal system monitor written in Python. It
shows live CPU, memory, disk, network, battery, and process information in a
Rich terminal dashboard.

The project also includes an optional FastAPI backend. The backend stores
snapshots in PostgreSQL, exposes authenticated API endpoints, and supports
background collection.

## Features

- Live terminal dashboard with automatic refresh
- CPU, memory, swap, disk, network, battery, and process metrics
- One-shot output for scripts with `--once`
- JSON output and file export
- Text and character analysis with `--count-text`
- JWT authentication and user roles for the backend
- PostgreSQL persistence through Prisma
- Snapshot history with pagination, filtering, and sorting
- API validation, CORS configuration, rate limiting, and safe error responses

## Requirements

- Python 3.10 or newer
- Docker, if you want to run the PostgreSQL backend locally

## Installation

```bash
git clone https://github.com/anzydev/ad-project.git
cd ad-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\activate
```

## Terminal monitor

Start the live dashboard:

```bash
python main.py
```

Useful commands:

```bash
python main.py --once
python main.py --json
python main.py --export snapshot.json
python main.py --count-text "hello world" --char l
python main.py --help
```

During live mode:

- `q` or `x` quits
- `r` refreshes immediately
- `+` and `-` change the refresh interval
- `p` or Space pauses and resumes updates

## Backend and PostgreSQL

The terminal monitor works without the backend. To run the API locally:

```bash
cp .env.example .env
docker compose up -d postgres
prisma migrate deploy --schema prisma/schema.prisma
prisma generate --schema prisma/schema.prisma
uvicorn ad_project.api.app:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is
available at `http://127.0.0.1:8000/docs`.

The main endpoints are:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
GET  /api/v1/health
POST /api/v1/snapshots
POST /api/v1/snapshots/collect
GET  /api/v1/snapshots
GET  /api/v1/admin/users
```

Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `.env` to create an administrator
when the API starts. Set `ENABLE_BACKGROUND_COLLECTION=true` to enable periodic
snapshot collection. Use a long random value for `JWT_SECRET_KEY` outside local
development.

## Project layout

```text
ad_project/
  api/          FastAPI routes, authentication, and database access
  collectors.py System metric collectors
  counter.py    Text analysis utilities
  exporter.py   Snapshot export helpers
  models.py     Snapshot dataclasses
  ui.py         Rich dashboard rendering
  utils.py      Formatting and terminal input helpers
prisma/         PostgreSQL schema and migrations
tests/          Unit and backend security tests
main.py         Direct terminal application entrypoint
```

## Data Engineering (DE) capstone submission

The database deliverables are collected in **[DE/README.md](DE/README.md)**: ER diagram, implemented Prisma schema and SQL migrations, application SQL queries with recorded outputs, integrity/transaction demonstrations, and the individual Q1–Q5 viva speaking and screen-demo guide (`DE/08_VIVA_DEMO.md`).

For the live demo, run `./START_DE_DEMO.command` on macOS or follow the setup steps in `DE/README.md`. The individual video must be **recorded and submitted separately** through the course form; pushing the repository does not submit the video.

## Tests

```bash
pytest -q
```

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
