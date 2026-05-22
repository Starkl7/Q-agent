"""WRDS database connection helper using named profiles, env vars, or ~/.pgpass."""

import json
import os
from pathlib import Path

import wrds

DEFAULT_WRDS_HOSTNAME = 'wrds-pgdata.wharton.upenn.edu'
DEFAULT_WRDS_PORT = '9737'
DEFAULT_WRDS_DBNAME = 'wrds'
DEFAULT_WRDS_USERNAME = None
DEFAULT_PROFILES_FILE = Path(__file__).resolve().parents[2] / '.wrds_profiles.json'

_connection = None
_connection_profile = None


def _normalize_profile_name(profile_name):
    if profile_name is None:
        return None

    profile_name = str(profile_name).strip()
    return profile_name or None


def set_connection_profile(profile_name):
    """Set the active named WRDS profile for future connections."""
    global _connection
    global _connection_profile

    normalized = _normalize_profile_name(profile_name)
    if normalized == _connection_profile:
        return normalized

    if _connection is not None:
        _connection.close()
        _connection = None

    _connection_profile = normalized
    return normalized


def _matches_pgpass_field(value, candidate):
    return value == '*' or value == str(candidate)


def _load_pgpass_credentials(hostname, port, dbname, username):
    """Return a password from ~/.pgpass when an entry matches the WRDS connection."""
    pgpass_path = Path(os.environ.get('PGPASSFILE', Path.home() / '.pgpass'))
    if not pgpass_path.exists():
        return None

    for raw_line in pgpass_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue

        parts = line.split(':', 4)
        if len(parts) != 5:
            continue

        file_host, file_port, file_db, file_user, file_password = parts
        if not _matches_pgpass_field(file_host, hostname):
            continue
        if not _matches_pgpass_field(file_port, port):
            continue
        if not _matches_pgpass_field(file_db, dbname):
            continue
        if not _matches_pgpass_field(file_user, username):
            continue

        return file_password

    return None


def _load_profiles_config():
    profiles_path = Path(os.environ.get('WRDS_PROFILES_FILE', DEFAULT_PROFILES_FILE))
    if not profiles_path.exists():
        return {}, profiles_path

    try:
        config = json.loads(profiles_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid WRDS profiles JSON in {profiles_path}: {exc}") from exc

    if not isinstance(config, dict):
        raise ValueError(f"WRDS profiles file must contain a JSON object: {profiles_path}")

    return config, profiles_path


def _load_named_profile(profile_name, config, profiles_path):
    profiles = config.get('profiles', {})
    if not isinstance(profiles, dict):
        raise ValueError(
            f"WRDS profiles file has invalid 'profiles' mapping: {profiles_path}"
        )

    if profile_name not in profiles:
        available_profiles = ', '.join(sorted(profiles)) if profiles else 'none'
        raise ValueError(
            f"WRDS profile '{profile_name}' not found in {profiles_path}. "
            f"Available profiles: {available_profiles}"
        )

    profile_settings = profiles[profile_name]
    if not isinstance(profile_settings, dict):
        raise ValueError(
            f"WRDS profile '{profile_name}' must map to an object in {profiles_path}"
        )

    return profile_settings


def _has_explicit_connection_identity():
    identity_keys = (
        'WRDS_HOSTNAME',
        'WRDS_PORT',
        'WRDS_DBNAME',
        'WRDS_USERNAME',
        'PGHOST',
        'PGPORT',
        'PGDATABASE',
        'PGUSER',
    )
    return any(os.environ.get(key) for key in identity_keys)


def _resolve_connection_settings():
    config, profiles_path = _load_profiles_config()

    explicit_profile = _normalize_profile_name(
        _connection_profile or os.environ.get('WRDS_PROFILE')
    )
    if explicit_profile:
        profile_name = explicit_profile
        profile_settings = _load_named_profile(profile_name, config, profiles_path)
    elif _has_explicit_connection_identity():
        profile_name = None
        profile_settings = {}
    else:
        default_profile = _normalize_profile_name(config.get('default_profile'))
        if default_profile:
            profile_name = default_profile
            profile_settings = _load_named_profile(profile_name, config, profiles_path)
        else:
            profile_name = None
            profile_settings = {}

    hostname = (
        profile_settings.get('hostname')
        or os.environ.get('WRDS_HOSTNAME')
        or os.environ.get('PGHOST')
        or DEFAULT_WRDS_HOSTNAME
    )
    port = (
        profile_settings.get('port')
        or os.environ.get('WRDS_PORT')
        or os.environ.get('PGPORT')
        or DEFAULT_WRDS_PORT
    )
    dbname = (
        profile_settings.get('dbname')
        or os.environ.get('WRDS_DBNAME')
        or os.environ.get('PGDATABASE')
        or DEFAULT_WRDS_DBNAME
    )
    username = (
        profile_settings.get('username')
        or os.environ.get('WRDS_USERNAME')
        or os.environ.get('PGUSER')
        or DEFAULT_WRDS_USERNAME
    )
    password = (
        os.environ.get('WRDS_PASSWORD')
        or os.environ.get('PGPASSWORD')
        or profile_settings.get('password')
    )

    if not password:
        password = _load_pgpass_credentials(hostname, port, dbname, username)

    return {
        'profile_name': profile_name,
        'hostname': hostname,
        'port': int(port),
        'dbname': dbname,
        'username': username,
        'password': password,
    }


def get_connection():
    """Get or create a singleton WRDS connection."""
    global _connection
    if _connection is None:
        settings = _resolve_connection_settings()

        connection_kwargs = {
            'wrds_hostname': settings['hostname'],
            'wrds_port': settings['port'],
            'wrds_dbname': settings['dbname'],
            'wrds_username': settings['username'],
        }
        if settings['password']:
            connection_kwargs['wrds_password'] = settings['password']

        _connection = wrds.Connection(**connection_kwargs)
    return _connection


def close_connection():
    """Close the singleton connection if open."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
