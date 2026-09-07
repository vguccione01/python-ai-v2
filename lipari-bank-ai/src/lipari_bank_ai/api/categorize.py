from fastapi import APIRouter
from lipari_bank_ai.services.categorize_service import categorize as categorize_service
from lipari_bank_ai.types.categorize import CategorizeRequest, CategorizeResponse


router = APIRouter(prefix="/api/ai", tags=["Categorize"])


@router.post("/categorize", response_model=CategorizeResponse)
async def categorize_endpoint(req: CategorizeRequest) -> CategorizeResponse:
    return await categorize_service(req)