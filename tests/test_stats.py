import os
import pytest

# Set required env vars before importing any bot modules
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("GEMINI_APIKEY", "test-key")
os.environ.setdefault("ADMIN_HANDLE", "testadmin")

import importlib, sys
# Load stats module directly to avoid triggering the full commands/__init__.py chain
_spec = importlib.util.spec_from_file_location(
    "stats_module",
    os.path.join(os.path.dirname(__file__), "..", "commands", "stats.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

parse_metric_id_from_sk = _mod.parse_metric_id_from_sk
extract_metric_ids = _mod.extract_metric_ids

SAMPLE_RESPONSE = {
    "items": [
        {"PK": "USER#rstave", "SK": "METRIC#account-comcast-401k", "entityType": "MetricInstance", "metricId": "account-comcast-401k", "name": "Comcast 401K Account", "sourceId": "comcast-401k", "templateId": "account"},
        {"PK": "USER#rstave", "SK": "METRIC#account-compushare", "entityType": "MetricInstance", "metricId": "account-compushare", "name": "CompuShare Account", "sourceId": "compushare", "templateId": "account"},
        {"PK": "USER#rstave", "SK": "METRIC#account-fidelity", "entityType": "MetricInstance", "metricId": "account-fidelity", "name": "Fidelity Account", "sourceId": "fidelity", "templateId": "account"},
        {"PK": "USER#rstave", "SK": "METRIC#account-schwab-common", "entityType": "MetricInstance", "metricId": "account-schwab-common", "name": "Schwab Common Account", "sourceId": "schwab-common", "templateId": "account"},
        {"PK": "USER#rstave", "SK": "METRIC#account-schwab-regular", "entityType": "MetricInstance", "metricId": "account-schwab-regular", "name": "Schwab Regular Account", "sourceId": "schwab-regular", "templateId": "account"},
        {"PK": "USER#rstave", "SK": "METRIC#blood-pressure", "entityType": "MetricInstance", "metricId": "blood-pressure", "name": "Blood Pressure", "sourceId": "monitor", "templateId": "blood-pressure"},
        {"PK": "USER#rstave", "SK": "METRIC#body-dimensions", "entityType": "MetricInstance", "metricId": "body-dimensions", "name": "Body dimensions", "sourceId": "report", "templateId": "body-dimensions"},
        {"PK": "USER#rstave", "SK": "METRIC#drinks-report", "entityType": "MetricInstance", "metricId": "drinks-report", "name": "Drinks", "sourceId": "report", "templateId": "drinks"},
        {"PK": "USER#rstave", "SK": "METRIC#steps-iphone", "entityType": "MetricInstance", "metricId": "steps-iphone", "name": "iPhone Steps", "sourceId": "iphone", "templateId": "steps"},
        {"PK": "USER#rstave", "SK": "METRIC#temp-garage", "entityType": "MetricInstance", "metricId": "temp-garage", "name": "Garage Temperature", "sourceId": "garage-sensor", "templateId": "temperature"},
        {"PK": "USER#rstave", "SK": "METRIC#weight-scale", "entityType": "MetricInstance", "metricId": "weight-scale", "name": "Weight", "sourceId": "scale", "templateId": "weight"},
    ]
}

EXPECTED_IDS = [
    "account-comcast-401k",
    "account-compushare",
    "account-fidelity",
    "account-schwab-common",
    "account-schwab-regular",
    "blood-pressure",
    "body-dimensions",
    "drinks-report",
    "steps-iphone",
    "temp-garage",
    "weight-scale",
]


class TestParseMetricIdFromSk:
    def test_standard_sk(self):
        assert parse_metric_id_from_sk("METRIC#weight-scale") == "weight-scale"

    def test_sk_with_multiple_hashes(self):
        # Only the first # is used as separator
        assert parse_metric_id_from_sk("METRIC#foo#bar") == "foo#bar"

    def test_sk_no_hash(self):
        assert parse_metric_id_from_sk("weight-scale") == "weight-scale"

    def test_sk_empty(self):
        assert parse_metric_id_from_sk("") == ""


class TestExtractMetricIds:
    def test_items_wrapper(self):
        result = extract_metric_ids(SAMPLE_RESPONSE)
        assert result == EXPECTED_IDS

    def test_data_wrapper(self):
        data = {"data": SAMPLE_RESPONSE["items"]}
        result = extract_metric_ids(data)
        assert result == EXPECTED_IDS

    def test_bare_list(self):
        result = extract_metric_ids(SAMPLE_RESPONSE["items"])
        assert result == EXPECTED_IDS

    def test_empty_dict(self):
        assert extract_metric_ids({}) == []

    def test_empty_list(self):
        assert extract_metric_ids([]) == []

    def test_falls_back_to_metric_id_when_no_sk(self):
        data = {"items": [{"metricId": "weight-scale"}]}
        assert extract_metric_ids(data) == ["weight-scale"]

    def test_weight_scale_present(self):
        result = extract_metric_ids(SAMPLE_RESPONSE)
        assert "weight-scale" in result

    def test_count(self):
        result = extract_metric_ids(SAMPLE_RESPONSE)
        assert len(result) == 11
