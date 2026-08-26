"""Database models and ORM configuration."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from aniflow.models import DownloadStatus

Base = declarative_base()

# Database file location
DB_PATH = Path("./aniflow_db.sqlite")


class SessionModel(Base):  # type: ignore
    """ORM model for download sessions."""

    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    series_name = Column(String, nullable=False)
    series_url = Column(String, nullable=False)
    source = Column(String, nullable=False)
    status = Column(String, default=DownloadStatus.PENDING.value)
    total_episodes = Column(Integer)
    completed_episodes = Column(Integer, default=0)
    failed_episodes = Column(Integer, default=0)
    output_dir = Column(String)
    quality = Column(Integer, default=1080)
    audio_lang = Column(String, default="jpn")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class EpisodeModel(Base):  # type: ignore
    """ORM model for episodes."""

    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    episode_num = Column(Integer, nullable=False)
    title = Column(String)
    url = Column(String)
    status = Column(String, default=DownloadStatus.PENDING.value)
    quality = Column(Integer)
    source = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    downloaded_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SegmentModel(Base):  # type: ignore
    """ORM model for HLS segments."""

    __tablename__ = "segments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    episode_id = Column(Integer, nullable=False)
    segment_index = Column(Integer, nullable=False)
    segment_hash = Column(String)  # SHA256 hash for dedup
    url = Column(String)
    source = Column(String)
    status = Column(String, default=DownloadStatus.PENDING.value)
    file_path = Column(String)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)


class LibraryModel(Base):  # type: ignore
    """ORM model for library entries."""

    __tablename__ = "library"

    id = Column(Integer, primary_key=True, autoincrement=True)
    series_name = Column(String, nullable=False, unique=True)
    series_url = Column(String)
    genres = Column(Text)  # JSON string
    rating = Column(Float)
    year = Column(Integer)
    season = Column(String)
    total_episodes = Column(Integer)
    watched_episodes = Column(Integer, default=0)
    user_rating = Column(Float)
    last_watched = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class WatchHistoryModel(Base):  # type: ignore
    """ORM model for watch history."""

    __tablename__ = "watch_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    library_id = Column(Integer, nullable=False)
    episode_num = Column(Integer, nullable=False)
    watched_at = Column(DateTime, default=datetime.now)
    watch_duration_seconds = Column(Integer)
    completed = Column(Boolean, default=False)


def init_database() -> None:
    """Initialize database and create tables."""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Get database session.

    Returns:
        SQLAlchemy session
    """
    engine = create_engine(f"sqlite:///{DB_PATH}")
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
