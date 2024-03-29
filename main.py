import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import video, subtitle, locale, google_language
from integration.webhook import minio_webhook
from config.database import engine
from config.exceptions.custom_exceptions import BusinessErrorException, InternalErrorException
from config.exceptions.exception_advice import handle_exception
from models import entities

app = FastAPI()

origins = [
    'http://localhost:3000'
]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

# Include router
app.include_router(video.router)
app.include_router(subtitle.router)
app.include_router(locale.router)
app.include_router(google_language.router)
app.include_router(minio_webhook.router)


# Include exception handler
app.add_exception_handler(BusinessErrorException, handler=handle_exception)
app.add_exception_handler(InternalErrorException, handler=handle_exception)

entities.Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def healthy():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
