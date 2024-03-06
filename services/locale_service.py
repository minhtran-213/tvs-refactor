from typing import List

from sqlalchemy.orm import Session

from models.entities import LocaleEntity


def get_all(db: Session):
    return db.query(LocaleEntity).all()


def get_by_code(db: Session, code: str) -> LocaleEntity:
    locale = db.query(LocaleEntity).filter(LocaleEntity.universal_code == code).first()
    return locale


def get_locale_by_code_like(db: Session, code: str) -> LocaleEntity:
    locales: List = db.query(LocaleEntity).filter(LocaleEntity.universal_code.like(f"%{code}%")).all()
    if len(locales) == 0:
        return get_by_code(db, "na-NA")
    return locales[0]
