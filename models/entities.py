from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum

from config.database import Base
from models.enums import ProcessStatus


class AbstractEntity:
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    created_by = Column(String)
    modified_by = Column(String)


class UserEntity(Base, AbstractEntity):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    password = Column(String)
    phone_number = Column(String)
    date_of_birth = Column(DateTime)
    gender = Column(String)
    role_code = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    created_by = Column(String)
    modified_by = Column(String)
    version = Column(Integer)


class GttsLanguageEntity(Base, AbstractEntity):
    __tablename__ = "gtts_languages"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    locale_id = Column(Integer, ForeignKey("locale.id"))
    code = Column(String)


class GoogleLanguageEntity(Base, AbstractEntity):
    __tablename__ = "google_languages"

    id = Column(Integer, primary_key=True)
    voice_name = Column(String)
    locale_id = Column(Integer, ForeignKey("locale.id"))
    gender = Column(String)


class LocaleEntity(Base, AbstractEntity):
    __tablename__ = "locale"

    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    universal_code = Column(String)


class VideoFileStoragesEntity(Base, AbstractEntity):
    __tablename__ = 'video_file_storages'
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String)
    file_name = Column(String)
    file_extension = Column(String)
    content_type = Column(String)
    process_status = Column(Enum(ProcessStatus))
    file_duration = Column(String)
    file_resolution = Column(String)
    input_locale_id = Column(Integer, ForeignKey('locale.id'))
    output_locale_id = Column(Integer, ForeignKey('locale.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    size = Column(String)
    external_file_path = Column(String)
    youtube_links = Column(String)


class SubtitleFileStorageEntity(Base):
    __tablename__ = "subtitle_file_storages"

    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    file_name = Column(String)
    file_extension = Column(String)
    locale_id = Column(Integer, ForeignKey("locale.id"))
    video_file_id = Column(Integer, ForeignKey("video_file_storages.id"))
    type = Column(String)
