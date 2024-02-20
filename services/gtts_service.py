from sqlalchemy.orm import Session

import locale_service
from models.entities import GttsLanguageEntity
from router import google_language


def update_by_id(db: Session):
    locales = locale_service.get_all(db)
    gtts_languages = db.query(GttsLanguageEntity).all()
    for gtts_language in gtts_languages:
        for locale in locales:
            if gtts_language.code in locale.universal_code:
                google_language.locale_id = locale.id
                db.query(GttsLanguageEntity).filter(GttsLanguageEntity.id == gtts_language.id).update(
                    {"locale_id": locale.id})
    db.commit()
