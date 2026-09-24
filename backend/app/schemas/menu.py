from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Item name cannot be empty")
    description: str | None = Field(None, max_length=255)
    price: float = Field(..., ge=0.0, description="Price must be non-negative")
    category: str = Field("General", min_length=1, max_length=50)
    image_url: str | None = Field(None, max_length=500)
    is_available: bool = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    price: float | None = Field(None, ge=0.0)
    category: str | None = Field(None, min_length=1, max_length=50)
    image_url: str | None = Field(None, max_length=500)
    is_available: bool | None = None


class MenuItemAvailabilityUpdate(BaseModel):
    is_available: bool


class MenuItemResponse(MenuItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class MenuItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: str = Field(min_length=1, max_length=80)
    is_available: bool = True

class MenuItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    is_available: bool | None = None

class AvailabilityUpdate(BaseModel):
    is_available: bool

class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; name: str; description: str; price: Decimal; category: str; is_available: bool
