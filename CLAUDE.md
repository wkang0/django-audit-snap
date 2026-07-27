# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run all tests:**
```bash
make test
# or explicitly:
python audit_log/tests/runtests.py
python audit_log/tests/runtests_custom_auth.py
```

**Run a specific test module:**
```bash
python audit_log/tests/runtests.py audit_log_tests.test_logging
python audit_log/tests/runtests.py audit_log_tests.test_manager
```

Both test runners self-configure Django settings (SQLite in-memory DB) — no external setup required.

## Architecture

This is a reusable Django app (`audit_log/`) that tracks model changes via two mechanisms:

**1. Lightweight auth stamping (`AuthStampedModel`)**
- `audit_log/models/__init__.py` — abstract base class with `created_by`, `created_with_session_key`, `modified_by`, `modified_with_session_key` fields
- Uses `CreatingUserField` / `LastUserField` (ForeignKey subclasses) and `CreatingSessionKeyField` / `LastSessionKeyField` (CharField subclasses) defined in `audit_log/models/fields.py`
- Fields self-register into `FieldRegistry` on `contribute_to_class`; the middleware reads the registry to know which fields to populate

**2. Full change history (`AuditLog` manager)**
- `audit_log/models/managers.py` — `AuditLog` is a descriptor/manager factory attached to a model class (e.g. `audit_log = AuditLog()`)
- On `class_prepared` signal, it dynamically creates a `<Model>AuditLogEntry` model (with copied fields + `action_id`, `action_date`, `action_user`, `action_type`) and connects `post_save`/`post_delete` signals to write log entries
- Action types: `"I"` (Insert/Created), `"U"` (Update/Changed), `"D"` (Delete/Deleted)
- `AuditLogDescriptor` makes `Model.audit_log` return a class-level manager or an instance-scoped manager filtered by PK
- Tracking can be disabled per-instance via `instance.audit_log.disable_tracking()` / `enable_tracking()`; globally via `DISABLE_AUDIT_LOG = True` in Django settings

**Middleware (`audit_log/middleware.py`)**
- `UserLoggingMiddleware` wires `pre_save`/`post_save` signals on each non-safe HTTP request, using `FieldRegistry` to inject the current user/session into the right fields
- `CreatingUserField` and `CreatingSessionKeyField` are only written on `created=True` in `post_save`, triggering a second `save()` with audit managers disabled to avoid double-logging
- `JWTAuthMiddleware` is a convenience wrapper for `django-rest-framework-jwt` JWT auth

**Registration (`audit_log/registration.py`)**
- `FieldRegistry` is a class-level dict (shared across instances) that maps field class → model → list of field instances, used by middleware to discover which models have audit fields

**Settings (`audit_log/settings.py`)**
- Single setting: `DISABLE_AUDIT_LOG` (default `False`) — disables all audit tracking globally when `True`

**Test structure**
- `audit_log/tests/runtests.py` — standard auth (`auth.User`)
- `audit_log/tests/runtests_custom_auth.py` — custom `AUTH_USER_MODEL = "audit_log.Employee"`
- Test models/views/urls live under `audit_log/tests/audit_log_tests/`

## Key design constraints

- The dynamically-created `<Model>AuditLogEntry` model's `AutoField` primary key is replaced with `IntegerField` to avoid multiple autofields; `OneToOneField`s become `ForeignKey` with `_unique=False`
- `FieldRegistry._registry` is a class-level dict — it persists for the Django process lifetime; all `FieldRegistry` instances share the same backing store
- M2M relation history is explicitly not supported
