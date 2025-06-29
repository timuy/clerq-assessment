
import requests
import os

from fastapi import APIRouter

from requests.adapters import HTTPAdapter

from src.schemas.settlement import SettlementRequest, SettlementResponse
from src.services.acme import AcmeService


router = APIRouter(prefix="/settlement", tags=["Settlements"])


@router.post("",
    summary="Get Settlement",
    description="Get Settlement",
)
async def get_settlement(request: SettlementRequest) -> SettlementResponse:
    try:
        pool_max_size = int(os.getenv("POOL_MAX_SIZE"))
    except ValueError:
        pool_max_size = 10

    adapter = HTTPAdapter(pool_maxsize=pool_max_size)

    session = requests.Session()
    session.mount("https://", adapter)

    amount = AcmeService.get_settlement_data(session, merchant = request.merchant, closing_date= request.closing_date)
    return SettlementResponse(amount=amount)
