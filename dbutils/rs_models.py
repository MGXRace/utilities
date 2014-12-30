"""
rs_models

Provides SQLAlchemy orm models for the racesow database
"""
from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


_Base = declarative_base()


_MAPTAG = Table('racesow_map_tags', _Base.metadata,
    Column('map_id', Integer, ForeignKey('racesow_map.id')),
    Column('tag_id', Integer, ForeignKey('racesow_tag.id'))
)


class Tag(_Base):
    """Tag for describing a map"""
    __tablename__ = 'racesow_tag'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    def __repr__(self):
        return '<Tag(id={}, name="{}")>'.format(self.id, self.name)


class Server(_Base):
    """Racesow Server Model"""
    __tablename__ = 'racesow_server'

    id = Column(Integer, primary_key=True)
    user = Column(Integer) # Todo - this is a foreign key to user
    address = Column(String(255))
    auth_key = Column(String(255))
    name = Column(String(255))
    simplified = Column(String(255))
    players = Column(Text)
    playtime = Column(BigInteger)
    races = Column(Integer)
    created = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Server(id={}, simp="{})>'.format(self.id, self.simplified)


class Map(_Base):
    """Racesow Map Model"""
    __tablename__ = 'racesow_map'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    pk3file = Column(String(255), default='')
    levelshotfile = Column(String(255), default='')
    enabled = Column(Boolean, default=True)
    races = Column(Integer, default=0)
    playtime = Column(BigInteger, default=0)
    created = Column(DateTime, default=lambda x: datetime.utcnow())
    oneliner = Column(String(255), default='')
    tags = relationship('Tag', secondary=_MAPTAG, backref='maps')

    def __repr__(self):
        return '<Map(id={}, name="{}")>'.format(self.id, self.name)


class Player(_Base):
    __tablename__ = 'racesow_player'

    id = Column(Integer, primary_key=True)
    user = Column(Integer) # Todo: this is a foreign key to user
    admin = Column(Boolean)
    name = Column(String(255))
    simplified = Column(String(255))
    playtime = Column(BigInteger)
    races = Column(Integer)
    maps = Column(Integer)
    points = Column(Integer)
    skill_m = Column(Float)
    skill_s = Column(Float)

    def __repr__(self):
        return '<Player(id={}, simp="{}")>'.format(self.id, self.simplified)
