# Contributing to django-audit-snap

Contributions are welcome. Please open an issue before submitting a PR for significant changes.

## Setup

Clone the repo and install in editable mode:

```bash
git clone https://github.com/wkang0/django-audit-snap.git
cd django-audit-snap
pip install -e .
```

## Running Tests

Both test suites must pass. They use an in-memory SQLite database — no external setup required.

```bash
# Run all tests
python audit_log/tests/runtests.py
python audit_log/tests/runtests_custom_auth.py

# Run a specific module
python audit_log/tests/runtests.py audit_log_tests.test_logging
python audit_log/tests/runtests.py audit_log_tests.test_manager
```

## Guidelines

- All PRs must pass both test suites
- Add tests for new behavior
- M2M relation history is not supported and is out of scope
- Keep changes focused — one concern per PR

## Releasing

Releases are published to PyPI automatically via GitHub Actions when a new release is created on GitHub. Only the maintainer creates releases.
