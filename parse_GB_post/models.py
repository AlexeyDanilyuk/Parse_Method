import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime

Base = declarative_base()


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String, unique=False, nullable=False)
    img_url = Column(String, nullable=False, unique=True)
    date_post = Column(DateTime, default=datetime.datetime.utcnow)
    writer_id = Column(Integer, ForeignKey("writer.id"))
    writer = relationship("Writer")
    tag_id = Column(Integer, ForeignKey("tag.id"))
    tag = relationship("Tag")


class Writer(Base):
    __tablename__ = "writer"
    id = Column(Integer, nullable=False, unique=True, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, autoincrement=True, primary_key=True)
    tag = Column(String, unique=False, nullable=False)


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, autoincrement=True, primary_key=True)
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post")
    text = Column(String)
    comment_author = Column(String, unique=False, nullable=False)
