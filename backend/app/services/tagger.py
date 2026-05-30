from typing import Any


def tag(record: dict[str, Any]) -> dict[str, Any]:
    """
    Apply keyword-based tags to a normalized record.
    Returns a dict with: industries, buyer_roles, pain_points, competitors, intent_stage.
    """
    raise NotImplementedError
