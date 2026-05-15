"""User accounts and sessions for Pebble.

Stores users at ``output/.users/<user_id>.json`` and an email→id lookup
at ``output/.users/_email_index.json``. Sessions live at
``output/.sessions/<token>.json`` and expire after :data:`SESSION_TTL`.

Password hashing uses stdlib :func:`hashlib.scrypt` — no new dependency,
production-acceptable parameters (N=16384, r=8, p=1). The hashing format
is versioned so we can bump parameters later without breaking old hashes.

Design notes:

- File-backed, not a database. Pebble runs as a single Python process and
  serves a small number of users in the MVP phase. A real DB lands when
  we deploy. Until then, JSON files are easy to inspect, back up, and
  copy between dev/prod.
- This module never talks to the network. Email verification, password
  resets, etc. live in the eventual transactional-email layer; this
  layer just stores accounts and validates passwords.
- Sessions are opaque random tokens, not JWTs. Server-side state means
  we can revoke instantly and don't need to leak any user info into the
  client.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import sys
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


# ---------- Config --------------------------------------------------------

SESSION_TTL = timedelta(days=30)
PASSWORD_RESET_TTL = timedelta(hours=1)
MIN_PASSWORD_LEN = 8

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# scrypt parameters. Match Python stdlib's accepted defaults; safe today.
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_DKLEN = 64


# ---------- Helpers -------------------------------------------------------

def _engine_output_dir() -> Path:
    """Resolve the engine's output dir. Lives behind the engine module so
    pytest's ``monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", ...)`` works
    for our tests the same way it does for history/projects.
    """
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path("output")


def _users_dir() -> Path:
    d = _engine_output_dir() / ".users"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sessions_dir() -> Path:
    d = _engine_output_dir() / ".sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sessions_index_path() -> Path:
    """Reverse-lookup: user_id → [token, ...]. Lets us revoke every
    session for a user without iterating every file in the sessions
    directory (O(active sessions) was hitting the whole server)."""
    return _sessions_dir() / "_by_user.json"


def _sessions_index_lock_path() -> Path:
    return _sessions_dir() / "_by_user.lock"


def _load_sessions_index() -> dict[str, list[str]]:
    p = _sessions_index_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_sessions_index(index: dict[str, list[str]]) -> None:
    p = _sessions_index_path()
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(index, indent=2), encoding="utf-8")
    try:
        os.replace(tmp, p)
    except Exception:
        # Best-effort — the index is a perf optimization, not the truth.
        try: tmp.unlink()
        except Exception: pass


def _password_reset_dir() -> Path:
    d = _engine_output_dir() / ".password_resets"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _email_index_path() -> Path:
    return _users_dir() / "_email_index.json"


def _load_email_index() -> dict[str, str]:
    p = _email_index_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_email_index(index: dict[str, str]) -> None:
    _email_index_path().write_text(json.dumps(index, indent=2), encoding="utf-8")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


# ---------- Password hashing ---------------------------------------------

def hash_password(plain: str) -> str:
    """Return a versioned, salted scrypt hash. Format::

        scrypt$N=<n>,r=<r>,p=<p>$<salt-hex>$<hash-hex>
    """
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        plain.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_DKLEN,
    )
    return f"scrypt$N={_SCRYPT_N},r={_SCRYPT_R},p={_SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time compare for the stored hash format."""
    try:
        scheme, params, salt_hex, digest_hex = hashed.split("$")
        if scheme != "scrypt":
            return False
        # Parse N=...,r=...,p=...
        kv = dict(part.split("=", 1) for part in params.split(","))
        n, r, p = int(kv["N"]), int(kv["r"]), int(kv["p"])
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.scrypt(
            plain.encode("utf-8"),
            salt=salt,
            n=n, r=r, p=p,
            dklen=len(expected),
        )
        return secrets.compare_digest(actual, expected)
    except Exception:
        return False


# ---------- Users ---------------------------------------------------------

@dataclass
class User:
    id:            str
    email:         str
    created_at:    str
    password_hash: str

    def to_public(self) -> dict:
        """Public-facing representation — never includes the password hash."""
        return {"id": self.id, "email": self.email, "created_at": self.created_at}


class AuthError(Exception):
    """Raised for any user-visible auth failure (bad email, weak password,
    duplicate signup, etc.). Carries a short, safe message."""


def _validate_email(email: str) -> str:
    e = _normalize_email(email)
    if not _EMAIL_RE.match(e):
        raise AuthError("Please enter a valid email address.")
    if len(e) > 254:
        raise AuthError("That email is too long.")
    return e


def _validate_password(password: str) -> None:
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LEN:
        raise AuthError(f"Password must be at least {MIN_PASSWORD_LEN} characters.")
    if len(password) > 1024:
        raise AuthError("That password is too long.")


def create_user(email: str, password: str) -> User:
    """Create a new user. Raises :class:`AuthError` for any validation or
    duplicate-email failure."""
    email_norm = _validate_email(email)
    _validate_password(password)

    index = _load_email_index()
    if email_norm in index:
        # Don't leak whether the email exists; phrase generically. Frontend
        # surfaces this in the same place as "wrong password" to keep
        # account enumeration noisy. Some apps prefer the explicit message —
        # we may switch later.
        raise AuthError("That email is already in use.")

    user = User(
        id=str(uuid.uuid4()),
        email=email_norm,
        created_at=datetime.now(timezone.utc).isoformat(),
        password_hash=hash_password(password),
    )
    (_users_dir() / f"{user.id}.json").write_text(
        json.dumps(asdict(user), indent=2), encoding="utf-8"
    )
    index[email_norm] = user.id
    _save_email_index(index)
    return user


def find_user_by_id(user_id: str) -> Optional[User]:
    if not user_id:
        return None
    path = _users_dir() / f"{user_id}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return User(**data)
    except Exception:
        return None


def find_user_by_email(email: str) -> Optional[User]:
    if not email:
        return None
    index = _load_email_index()
    user_id = index.get(_normalize_email(email))
    if not user_id:
        return None
    return find_user_by_id(user_id)


def authenticate(email: str, password: str) -> Optional[User]:
    """Return the user if email + password match, else None. Performs a
    dummy hash on the miss path so the lookup time doesn't leak whether
    the email exists."""
    user = find_user_by_email(email)
    if not user:
        # Burn a hash to keep the failure path's timing similar to a hit.
        hash_password("dummy-to-equalize-timing")
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# ---------- Sessions ------------------------------------------------------

@dataclass
class Session:
    token:      str
    user_id:    str
    created_at: str
    expires_at: str

    @property
    def is_expired(self) -> bool:
        try:
            return datetime.fromisoformat(self.expires_at) <= datetime.now(timezone.utc)
        except Exception:
            return True


def create_session(user_id: str) -> Session:
    now = datetime.now(timezone.utc)
    sess = Session(
        token=secrets.token_urlsafe(32),
        user_id=user_id,
        created_at=now.isoformat(),
        expires_at=(now + SESSION_TTL).isoformat(),
    )
    (_sessions_dir() / f"{sess.token}.json").write_text(
        json.dumps(asdict(sess), indent=2), encoding="utf-8"
    )
    # Maintain the reverse index so revoke_all_sessions_for can do its
    # work in O(sessions for this user) instead of O(every session file).
    index = _load_sessions_index()
    tokens = index.get(user_id, [])
    if sess.token not in tokens:
        tokens.append(sess.token)
        index[user_id] = tokens
        _save_sessions_index(index)
    return sess


def get_session(token: str) -> Optional[Session]:
    """Return the (non-expired) session for ``token``, or None. Expired
    sessions are deleted on read so the on-disk store self-cleans."""
    if not token or not isinstance(token, str):
        return None
    path = _sessions_dir() / f"{token}.json"
    if not path.exists():
        return None
    try:
        sess = Session(**json.loads(path.read_text(encoding="utf-8")))
    except Exception:
        return None
    if sess.is_expired:
        try:
            path.unlink()
        except Exception:
            pass
        return None
    return sess


def revoke_session(token: str) -> bool:
    """Delete a session. Returns True if it existed."""
    path = _sessions_dir() / f"{token}.json"
    # Capture user_id (if any) so we can keep the reverse index honest.
    user_id: Optional[str] = None
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            user_id = data.get("user_id")
        except Exception:
            pass
        try:
            path.unlink()
        except Exception:
            return False
        if user_id:
            _drop_token_from_index(user_id, token)
        return True
    return False


def _drop_token_from_index(user_id: str, token: str) -> None:
    """Remove ``token`` from the reverse index for ``user_id``."""
    index = _load_sessions_index()
    tokens = index.get(user_id)
    if not tokens:
        return
    try:
        tokens.remove(token)
    except ValueError:
        return
    if tokens:
        index[user_id] = tokens
    else:
        index.pop(user_id, None)
    _save_sessions_index(index)


def revoke_all_sessions_for(user_id: str) -> int:
    """Revoke every session belonging to a user. Returns count revoked.

    Reads the reverse index (output/.sessions/_by_user.json) instead of
    walking the whole sessions directory — O(sessions for this user)
    not O(every active session). NotebookLM flagged the original walk
    as a server-wide DoS vector at scale.

    If the index doesn't exist yet (legacy sessions written before this
    landed) we fall back to the walk so we still revoke correctly. The
    walk path also rebuilds the index for next time.
    """
    if not user_id:
        return 0
    index = _load_sessions_index()
    tokens = list(index.get(user_id, []))
    if tokens:
        count = 0
        for token in tokens:
            path = _sessions_dir() / f"{token}.json"
            try:
                path.unlink()
                count += 1
            except FileNotFoundError:
                pass
            except Exception:
                pass
        index.pop(user_id, None)
        _save_sessions_index(index)
        return count

    # Fallback: walk the directory. Slow but correct for legacy state.
    count = 0
    rebuilt: dict[str, list[str]] = {}
    for path in _sessions_dir().glob("*.json"):
        if path.name.startswith("_"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        owner = data.get("user_id")
        token = data.get("token") or path.stem
        if owner == user_id:
            try:
                path.unlink()
                count += 1
            except Exception:
                pass
        elif owner:
            rebuilt.setdefault(owner, []).append(token)
    if rebuilt or count:
        _save_sessions_index(rebuilt)
    return count


# ---------- Password reset tokens ----------------------------------------

@dataclass
class PasswordResetToken:
    token:      str
    user_id:    str
    created_at: str
    expires_at: str

    @property
    def is_expired(self) -> bool:
        try:
            return datetime.fromisoformat(self.expires_at) <= datetime.now(timezone.utc)
        except Exception:
            return True


def create_password_reset_token(user_id: str) -> PasswordResetToken:
    """Generate and persist a one-time reset token for ``user_id``."""
    now = datetime.now(timezone.utc)
    tok = PasswordResetToken(
        token=secrets.token_urlsafe(32),
        user_id=user_id,
        created_at=now.isoformat(),
        expires_at=(now + PASSWORD_RESET_TTL).isoformat(),
    )
    (_password_reset_dir() / f"{tok.token}.json").write_text(
        json.dumps(asdict(tok), indent=2), encoding="utf-8"
    )
    return tok


def get_password_reset_token(token: str) -> Optional[PasswordResetToken]:
    """Look up a reset token. Returns None if missing, malformed, or
    expired. Expired tokens are deleted on read so the store self-cleans."""
    if not token or not isinstance(token, str):
        return None
    path = _password_reset_dir() / f"{token}.json"
    if not path.exists():
        return None
    try:
        rec = PasswordResetToken(**json.loads(path.read_text(encoding="utf-8")))
    except Exception:
        return None
    if rec.is_expired:
        try: path.unlink()
        except Exception: pass
        return None
    return rec


def consume_password_reset_token(token: str) -> Optional[PasswordResetToken]:
    """Look up the token and delete it. Returns the record on hit, None
    on miss/expired/already-consumed.

    Race-safe via atomic rename: we move the token file to a unique
    consumed-name *before* reading it. ``os.replace`` is atomic on
    POSIX and Windows, so only one of N concurrent /api/auth/reset
    callers wins the rename — the others get FileNotFoundError and
    return None. NotebookLM flagged the prior read-then-unlink as
    a TOCTOU window allowing double-reset.
    """
    if not token or not isinstance(token, str):
        return None
    src = _password_reset_dir() / f"{token}.json"
    # Per-call destination so concurrent callers don't collide.
    dst = _password_reset_dir() / f".consumed-{secrets.token_hex(8)}-{token}.json"
    try:
        os.replace(src, dst)
    except FileNotFoundError:
        return None
    except Exception:
        return None
    try:
        rec = PasswordResetToken(**json.loads(dst.read_text(encoding="utf-8")))
    except Exception:
        # File was moved but unreadable; treat as miss and clean up.
        try: dst.unlink()
        except Exception: pass
        return None
    # Clean up the consumed copy regardless of expiry.
    try: dst.unlink()
    except Exception: pass
    if rec.is_expired:
        return None
    return rec


def update_user_password(user_id: str, new_password: str) -> Optional[User]:
    """Re-hash and persist a user's password. Returns the updated User
    (or None if user_id is unknown). Caller is responsible for revoking
    sessions and consuming the reset token."""
    _validate_password(new_password)
    user = find_user_by_id(user_id)
    if not user:
        return None
    user.password_hash = hash_password(new_password)
    (_users_dir() / f"{user.id}.json").write_text(
        json.dumps(asdict(user), indent=2), encoding="utf-8"
    )
    return user


def session_to_user(token: str) -> Optional[User]:
    sess = get_session(token)
    if not sess:
        return None
    return find_user_by_id(sess.user_id)


# ---------- Cookie helpers -----------------------------------------------

SESSION_COOKIE_NAME = "pebble_session"


def cookie_for_session(token: str, secure: bool = False) -> str:
    """Build a Set-Cookie header value for a new session. ``secure`` should
    be True in production (HTTPS); False is needed for local dev over HTTP."""
    parts = [
        f"{SESSION_COOKIE_NAME}={token}",
        f"Max-Age={int(SESSION_TTL.total_seconds())}",
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
    ]
    if secure:
        parts.append("Secure")
    return "; ".join(parts)


def clear_cookie() -> str:
    """Set-Cookie header value that clears the session cookie."""
    return f"{SESSION_COOKIE_NAME}=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax"


def parse_session_token(cookie_header: str) -> str:
    """Extract our session token from a raw Cookie header."""
    if not cookie_header:
        return ""
    for part in cookie_header.split(";"):
        kv = part.strip().split("=", 1)
        if len(kv) == 2 and kv[0] == SESSION_COOKIE_NAME:
            return kv[1]
    return ""
