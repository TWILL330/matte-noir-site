import csv
import io
import json
from typing import Any

from app.providers.base import RedditDataProvider


class ManualImportProvider(RedditDataProvider):
    """
    Loads records from an uploaded CSV or JSON file.
    This is the only active provider in the MVP.
    """

    def fetch(self, **kwargs) -> list[dict[str, Any]]:
        raise NotImplementedError("Use from_csv() or from_json() directly.")

    @staticmethod
    def from_csv(content: bytes) -> list[dict[str, Any]]:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        return [dict(row) for row in reader]

    @staticmethod
    def from_json(content: bytes) -> list[dict[str, Any]]:
        data = json.loads(content.decode("utf-8"))
        return data if isinstance(data, list) else [data]
