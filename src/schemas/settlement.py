
from pydantic import BaseModel

from datetime import date

class SettlementRequest(BaseModel):
    """Settlement Request Schema."""

    merchant: str
    closing_date: date


class SettlementResponse(BaseModel):
    """Settlement Respnse Schema."""

    amount: float
