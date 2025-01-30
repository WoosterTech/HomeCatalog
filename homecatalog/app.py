from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from homecatalog.models import ThingType


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///homecatalog.db"
db = SQLAlchemy(app, model_class=Base)


class DbPublisher(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class DbArtist(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class DbCategory(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class DbMechanism(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class DbFamily(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class DbThing(Base):  # see https://boardgamegeek.com/wiki/page/BGG_XML_API2
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    bgg_id: Mapped[int] = mapped_column(unique=True)
    thing_type: Mapped[ThingType] = mapped_column()
    thumbnail: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column()
    publisher_id: Mapped[int] = mapped_column()
    artist_id: Mapped[int] = mapped_column()
    category_id: Mapped[int] = mapped_column()
    mechanism_id: Mapped[int] = mapped_column()
    family_id: Mapped[int] = mapped_column()
    year: Mapped[int] = mapped_column()
    min_players: Mapped[int] = mapped_column()
    max_players: Mapped[int] = mapped_column()
    min_age: Mapped[int] = mapped_column()
    playing_time: Mapped[int] = mapped_column()
    bgg_rank: Mapped[int] = mapped_column()
