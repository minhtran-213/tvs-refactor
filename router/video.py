from fastapi import APIRouter

router = APIRouter(
    prefix="/videos",
    tags=["videos"]
)


@router.get("/filter")
async def get_all():
    return {"data": "All videos"}


@router.post("/files")
async def create():
    return {"data": "File created"}


@router.post("/youtube-links")
async def upload_by_youtube():
    return {"data": "Youtube link uploaded"}
