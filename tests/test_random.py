import os
import sys


os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("GEMINI_APIKEY", "test-key")
os.environ.setdefault("ADMIN_HANDLE", "testadmin")

import importlib.util


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


_spec = importlib.util.spec_from_file_location(
    "random_module",
    os.path.join(os.path.dirname(__file__), "..", "commands", "random_number.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

parse_random_upper_bound = _mod.parse_random_upper_bound


class TestParseRandomUpperBound:
    def test_defaults_to_100(self):
        assert parse_random_upper_bound([]) == 100

    def test_uses_positive_integer_argument(self):
        assert parse_random_upper_bound(["6"]) == 6

    def test_rejects_zero(self):
        try:
            parse_random_upper_bound(["0"])
            assert False, "expected ValueError"
        except ValueError:
            pass

    def test_rejects_negative_values(self):
        try:
            parse_random_upper_bound(["-4"])
            assert False, "expected ValueError"
        except ValueError:
            pass

    def test_rejects_non_integer_values(self):
        try:
            parse_random_upper_bound(["cat"])
            assert False, "expected ValueError"
        except ValueError:
            pass