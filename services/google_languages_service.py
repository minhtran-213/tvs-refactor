from sqlalchemy.orm.session import Session

from models.entities import GoogleLanguageEntity
from services import locale_service


def update_locale_id(db: Session):
    locales = locale_service.get_all(db)
    google_languages = db.query(GoogleLanguageEntity).all()
    for google_language in google_languages:
        for locale in locales:
            if locale.universal_code in google_language.voice_name:
                google_language.locale_id = locale.id
                db.query(GoogleLanguageEntity).filter(GoogleLanguageEntity.id == google_language.id).update(
                    {"locale_id": locale.id})
    db.commit()
