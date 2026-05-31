from abc import ABC, abstractmethod
from typing import Any


class RedditDataProvider(ABC):
    """
    Interface for all Reddit data sources.

    To add a new source (e.g. approved Reddit API, Pushshift export):
      1. Subclass RedditDataProvider
      2. Implement fetch() to return a list of raw record dicts
      3. Register it in PROVIDER_REGISTRY below

    Raw dicts are passed directly to services.normalizer.normalize(),
    which handles field aliasing and type coercion, so providers don't
    need to conform to the internal schema — just return whatever the
    source gives you.
    """

    @abstractmethod
    def fetch(self, **kwargs) -> list[dict[str, Any]]:
        """Return a list of raw records as plain dicts."""
        ...


# Registry maps string identifiers to provider classes.
# Used by future tooling (scheduled jobs, webhooks, etc.) to select a provider.
PROVIDER_REGISTRY: dict[str, type[RedditDataProvider]] = {}
