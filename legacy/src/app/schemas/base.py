from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema for all Pydantic models."""

    model_config = ConfigDict(from_attributes=True)
