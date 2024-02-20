from sqlalchemy.orm import Session

from models.entities import LocaleEntity


def get_all(db: Session):
    return db.query(LocaleEntity).all()


def get_by_code(db: Session, code: str):
    locale = db.query(LocaleEntity).filter(LocaleEntity.universal_code == code).first()
    return locale
