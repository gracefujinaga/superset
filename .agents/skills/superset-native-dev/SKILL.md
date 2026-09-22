---
name: superset-native-dev
description: Run Apache Superset natively (no Docker) for development and testing - Python 3.11 venv with SQLite metadata DB, frontend dev server, unit tests, pre-commit. Use when docker compose is unavailable (e.g. Docker Hub rate limits) or when you need to run backend/frontend tests.
---

# Superset native development (no Docker)

`docker compose up` is the documented path, but it needs Docker Hub access. This is
the fallback that works on a plain Ubuntu box with ~7 GB RAM.

## Backend

```bash
# Python >= 3.11 is required (pyproject.toml). Use uv to get one if the host is older.
sudo apt-get install -y build-essential pkg-config default-libmysqlclient-dev libpq-dev \
  libssl-dev libffi-dev libsasl2-dev libldap2-dev zstd
uv venv --python 3.11 .venv && source .venv/bin/activate
uv pip install -r requirements/development.txt -e .

# Config lives OUTSIDE the repo. Never commit it.
mkdir -p ~/.superset && cat > ~/.superset/superset_config.py <<'EOF'
import os
SECRET_KEY = "local-dev-only-secret-key-change-me"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.expanduser('~')}/.superset/superset.db"
WTF_CSRF_ENABLED = True
FEATURE_FLAGS = {"ALERT_REPORTS": False}
EOF
export SUPERSET_CONFIG_PATH=~/.superset/superset_config.py FLASK_APP=superset

superset db upgrade
superset fab create-admin --username admin --firstname a --lastname d --email admin@example.com --password admin
superset init
superset load-examples          # optional, ~5 min
superset run -p 8088 --with-threads --reload --debugger
curl -f http://localhost:8088/health   # -> OK
```

SQLite means no Celery/Redis: async queries, alerts and reports are off. Login is
`admin` / `admin`.

## Frontend

```bash
cd superset-frontend
nvm use 24 && npm i -g npm@11        # package-lock requires npm 11; npm 10 fails `npm ci`
npm ci
DISABLE_TS_CHECKER=true npm run dev-server   # TS checker OOMs below ~8 GB
```

Serves on http://localhost:9000 and proxies the API to :8088.

## Tests

```bash
# Backend unit tests (no DB needed). --timeout is NOT available (pytest-timeout not installed).
pytest tests/unit_tests -q -p no:randomly
pytest tests/unit_tests -q -p no:randomly -n 2 --dist loadfile   # parallel; -n 4 gets OOM-killed on 7 GB

# Integration tests need Postgres + Redis (docker compose) - do not run them natively.

# Frontend
cd superset-frontend && npm run test -- path/to/file.test.tsx
```

## Pre-commit

```bash
pre-commit install
pre-commit run --files <changed files>     # what CI runs; mypy/ruff/eslint/license headers
```

New source files need the ASF license header; `.md` docs under `docs/` use an HTML
comment header (see `docs/developer_docs/contributing/development-setup.md`).
