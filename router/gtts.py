from fastapi import APIRouter, status, Depends
from config.database import get_db

router = APIRouter(
    prefix='/gtts',
    tags=['gtts']
)


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
async def update_locale_id(db: Depends(get_db)):
    pass
