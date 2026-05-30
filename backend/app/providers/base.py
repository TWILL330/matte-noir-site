from abc import ABC, abstractmethod
from typing import Any


class RedditDataProvider(ABC):
    """
    Interface for all Reddit data sources.
    Implement this to add a new source (e.g. approved Reddit API, Pushshift).
    """

    @abstractmethod
    def fetch(self, **kwargs) -> list[dict[str, Any]]:
        """Return a list of raw records as plain dicts."""
        ...
