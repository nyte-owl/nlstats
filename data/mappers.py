from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class ConversionRule(Base):
    __tablename__ = "conversion_rule"
    __table_args__ = {"schema": "youtube"}

    id = Column(Integer, primary_key=True)
    parsed_title = Column(String, nullable=False)
    final_title = Column(String, nullable=False)

    def __repr__(self):
        return (
            "ConversionRule<["
            f"id={self.id}, "
            f"parsed_title={self.parsed_title}, "
            f"final_title={self.final_title} "
            "]>"
        )


class CollectionEvent(Base):
    __tablename__ = "collection_event"
    __table_args__ = {"schema": "youtube"}

    id = Column(Integer, primary_key=True)
    pull_datetime = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    complete = Column(Boolean, nullable=False, default=False)

    raw_data = relationship("RawData", back_populates="collection_event")
    processed_stats = relationship("ProcessedStat", back_populates="collection_event")

    def __repr__(self):
        return (
            "CollectionEvent<["
            f"id={self.id}, "
            f"pull_datetime={self.pull_datetime}, "
            f"complete={self.complete} "
            "]>"
        )


class Video(Base):
    __tablename__ = "video"
    __table_args__ = {"schema": "youtube"}

    unique_youtube_id = Column(String, nullable=False, primary_key=True)
    publish_date = Column(DateTime)
    title = Column(String)
    description = Column(String)
    game = Column(String)
    duration_seconds = Column(Integer)

    processed_stats = relationship("ProcessedStat", back_populates="video_info")

    def __repr__(self):
        desc = f"{self.description[:30]}[...]" if self.description else self.description
        return (
            "Video<["
            f"unique_youtube_id={self.unique_youtube_id}, "
            f"publish_date={self.publish_date}, "
            f"title={self.title}, "
            f"description={desc}, "
            f"game={self.game}, "
            f"duration_seconds={self.duration_seconds} "
            "]>"
        )


class RawData(Base):
    __tablename__ = "raw_data"
    __table_args__ = {"schema": "youtube"}

    id = Column(Integer, primary_key=True)
    video_id = Column(
        String, ForeignKey("youtube.video.unique_youtube_id"), nullable=False
    )
    collection_event_id = Column(
        Integer, ForeignKey("youtube.collection_event.id"), nullable=False
    )
    kind = Column(String, nullable=False)
    etag = Column(String, nullable=False)
    snippet = Column(String, nullable=False)
    content_details = Column(String, nullable=False)
    statistics = Column(String, nullable=False)

    collection_event = relationship("CollectionEvent", back_populates="raw_data")

    def __repr__(self):
        return (
            "RawData<["
            f"id={self.id}, "
            f"video_id={self.video_id}, "
            f"collection_event_id={self.collection_event_id}, "
            f"kind={self.kind}, "
            f"etag={self.etag}, "
            f"snippet={self.snippet}, "
            f"content_details={self.content_details}, "
            f"statistics={self.statistics} "
            "]>"
        )


class ProcessedStat(Base):
    __tablename__ = "processed_stat"
    __table_args__ = {"schema": "youtube"}

    id = Column(Integer, primary_key=True)
    video_id = Column(
        String, ForeignKey("youtube.video.unique_youtube_id"), nullable=False
    )
    collection_event_id = Column(
        Integer, ForeignKey("youtube.collection_event.id"), nullable=False
    )
    views = Column(Integer, nullable=False)
    likes = Column(Integer, nullable=False)
    comments = Column(Integer, nullable=False)

    collection_event = relationship("CollectionEvent", back_populates="processed_stats")
    video_info = relationship("Video", back_populates="processed_stats")

    def __repr__(self):
        return (
            "ProcessedStat<["
            f"video_id={self.video_id}, "
            f"collection_event_id={self.collection_event_id}, "
            f"views={self.views}, "
            f"likes={self.likes}, "
            f"comments={self.comments}, "
            "]>"
        )
