# PitchBlack

PitchBlack generates short tactical football videos from structured match data.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Run Tests

```bash
pytest
```

## Run A Local Smoke Workflow

```bash
python -m shorts.main
```

## Render A Fixture Short

```bash
python -m shorts.workflows.run_local_fixture
```
