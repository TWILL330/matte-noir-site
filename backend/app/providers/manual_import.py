import csv
import io
import json
from typing import Any

from app.providers.base import PROVIDER_REGISTRY, RedditDataProvider


class ManualImportProvider(RedditDataProvider):
    """
    Loads records from an uploaded CSV or JSON file.
    This is the only active provider in the MVP.

    CSV: expects a header row; any column order is accepted.
    JSON: expects a JSON array of objects, or a single object.

    Field aliasing (e.g. 'score' → 'reddit_score') is handled downstream
    by services.normalizer, not here.
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


PROVIDER_REGISTRY["manual"] = ManualImportProvider
