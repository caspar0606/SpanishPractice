"""Per-user JSON storage: where files may be written, and how.

A username arrives from the request body and becomes a filename, so it decides a
filesystem path. These tests pin down that it can only ever name a file directly
inside the data directory, and that a write either lands completely or not at all.
"""

import json
import os

import pytest

from src.domain.models.user import User
from src.domain.utils import initialise_progress
from src.infrastructure.persistence import file_storage
from src.infrastructure.persistence.file_storage import (
    create_new_user_file,
    load_user_state,
    save_user_state,
    user_file_path,
)


@pytest.fixture(autouse=True)
def userdata(tmp_path, monkeypatch):
    """Point storage at a scratch directory for every test."""
    monkeypatch.setenv("USERDATA_DIR", str(tmp_path))
    return tmp_path


def make_user(name: str = "tester") -> User:
    return User(name=name, progress=initialise_progress(), first_time=True)


class TestUsernameSafety:
    @pytest.mark.parametrize(
        "username",
        [
            "../pwned",
            "../../pwned",
            r"..\..\pwned",
            "sub/dir",
            r"sub\dir",
            "/etc/passwd",
            r"C:\Windows\System32\config",
            "~/.ssh/id_rsa",
            "..",
            ".",
            ".hidden",
            "",
            "with space",
            "semi;colon",
            "null\x00byte",
            "a" * 65,
        ],
    )
    def test_unsafe_usernames_are_rejected(self, username):
        with pytest.raises(ValueError):
            user_file_path(username)

    @pytest.mark.parametrize(
        "username", ["tester", "Rudra", "user.name", "user_name", "user-name", "u", "9lives"]
    )
    def test_ordinary_usernames_are_accepted(self, username, userdata):
        path = user_file_path(username)

        assert path.parent.resolve() == userdata.resolve()
        assert path.name == f"{username}.json"

    def test_a_traversing_username_writes_nothing_outside_the_directory(self, userdata):
        """Regression: this used to create a file two levels above userdata/."""
        escapee = make_user("../../pwned")

        with pytest.raises(ValueError):
            save_user_state(escapee)

        assert not (userdata.parent.parent / "pwned.json").exists()

    def test_a_traversing_username_cannot_be_read_either(self):
        with pytest.raises(ValueError):
            load_user_state("../../../etc/passwd")


class TestRoundTrip:
    def test_a_saved_user_loads_back(self):
        user = make_user()
        user.progress.topics["travel"].total_attempts = 3

        save_user_state(user)
        loaded = load_user_state("tester")

        assert loaded is not None
        assert loaded.name == "tester"
        assert loaded.progress.topics["travel"].total_attempts == 3

    def test_missing_user_loads_as_none(self):
        assert load_user_state("nobody") is None

    def test_saving_twice_overwrites_rather_than_appends(self, userdata):
        save_user_state(make_user())
        save_user_state(make_user())

        content = (userdata / "tester.json").read_text(encoding="utf-8")
        assert json.loads(content)["name"] == "tester"


class TestAtomicWrites:
    def test_a_failed_write_leaves_the_previous_file_intact(self, userdata, monkeypatch):
        """A crash partway through must not destroy existing progress."""
        original = make_user()
        original.progress.topics["travel"].total_attempts = 7
        save_user_state(original)

        def boom(*args, **kwargs):
            raise OSError("disk full")

        monkeypatch.setattr(file_storage.os, "replace", boom)

        doomed = make_user()
        doomed.progress.topics["travel"].total_attempts = 999
        with pytest.raises(OSError):
            save_user_state(doomed)

        survivor = load_user_state("tester")
        assert survivor.progress.topics["travel"].total_attempts == 7

    def test_a_failed_write_leaves_no_temp_files_behind(self, userdata, monkeypatch):
        save_user_state(make_user())

        monkeypatch.setattr(
            file_storage.os, "replace", lambda *a, **k: (_ for _ in ()).throw(OSError())
        )
        with pytest.raises(OSError):
            save_user_state(make_user())

        assert [p.name for p in userdata.iterdir()] == ["tester.json"]


class TestUserCreation:
    def test_creating_a_new_user_makes_the_file(self, userdata):
        assert create_new_user_file("fresh") is None
        assert (userdata / "fresh.json").exists()

    def test_creating_an_existing_user_reports_the_clash(self):
        create_new_user_file("taken")

        assert create_new_user_file("taken") == 1

    def test_an_existing_file_is_not_truncated_by_a_second_create(self, userdata):
        """The exclusive create must not clobber the file it refused to replace."""
        user = make_user("taken")
        user.progress.topics["travel"].total_attempts = 5
        save_user_state(user)

        assert create_new_user_file("taken") == 1
        assert load_user_state("taken").progress.topics["travel"].total_attempts == 5

    def test_an_unsafe_username_cannot_be_created(self):
        with pytest.raises(ValueError):
            create_new_user_file("../../pwned")
