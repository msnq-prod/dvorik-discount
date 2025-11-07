from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from app.db.models.loyalty import Client


class SegmentationService:
    def _parse_condition(self, condition: dict):
        field = condition["field"]
        op = condition["op"]
        value = condition["value"]

        column = getattr(Client, field)

        if op == "==":
            return column == value
        if op == "!=":
            return column != value
        if op == ">":
            return column > value
        if op == ">=":
            return column >= value
        if op == "<":
            return column < value
        if op == "<=":
            return column <= value
        if op == "in":
            return column.in_(value)
        if op == "contains":
            return column.contains(value)
        raise ValueError(f"Unsupported operator: {op}")

    def _build_query(self, filters: dict):
        if "and" in filters:
            return and_(*[self._build_query(f) for f in filters["and"]])
        if "or" in filters:
            return or_(*[self._build_query(f) for f in filters["or"]])
        return self._parse_condition(filters)

    def get_client_ids(self, db: Session, *, audience_filter: dict) -> list[int]:
        if not audience_filter:
            return []

        query = select(Client.id).where(self._build_query(audience_filter))
        return db.scalars(query).all()
