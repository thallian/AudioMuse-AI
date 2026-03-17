import pytest
from config import get_config, ConfigError


def test_get_config_file_not_found(monkeypatch):
    """
    Test that ConfigError is raised when the _FILE path does not exist.
    """
    monkeypatch.setenv("MY_SECRET_FILE", "/path/to/nonexistent/file")
    with pytest.raises(ConfigError) as excinfo:
        get_config("MY_SECRET")
    assert "Failed to read config from file" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, FileNotFoundError)


def test_get_config_permission_denied(monkeypatch, tmp_path):
    """
    Test that ConfigError is raised when the file cannot be read due to permissions.
    """
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret")
    secret_file.chmod(0o200)
    monkeypatch.setenv("MY_SECRET_FILE", str(secret_file))

    with pytest.raises(ConfigError) as excinfo:
        get_config("MY_SECRET")
    assert "Failed to read config from file" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, PermissionError)


def test_get_config_path_is_directory(monkeypatch, tmp_path):
    """
    Test that ConfigError is raised when the _FILE path is a directory.
    """
    secret_dir = tmp_path / "a_directory"
    secret_dir.mkdir()

    monkeypatch.setenv("MY_SECRET_FILE", str(secret_dir))

    with pytest.raises(ConfigError) as excinfo:
        get_config("MY_SECRET")
    assert "Failed to read config from file" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, IsADirectoryError)


def test_get_config_from_file(monkeypatch, tmp_path):
    """
    Test that a value from a file is read if _FILE var is set (and not the env var value).
    """
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret")
    secret_file.chmod(0o400)

    monkeypatch.setenv("MY_SECRET", "no secret")
    monkeypatch.setenv("MY_SECRET_FILE", str(secret_file))

    value = get_config("MY_SECRET")
    assert value == "secret"


def test_get_config_from_env(monkeypatch):
    """
    Test that a value from an env config is read.
    """
    monkeypatch.setenv("MY_CONFIG", "config_value")
    value = get_config("MY_CONFIG")
    assert value == "config_value"


def test_get_config_default_from_env():
    """
    Test that a default value from an env config is read.
    """
    value = get_config("MY_CONFIG", "default_value")
    assert value == "default_value"
