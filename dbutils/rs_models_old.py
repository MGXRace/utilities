"""
rs_models_old

Provides SQLAlchemy orm models for the pre-1.1 racesow database
"""
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
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

_Base = declarative_base()
_map_status_choices = ['enabled', 'disabled', 'new', 'true', 'false']
_enum_bool = ['true', 'false']


class Player(_Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    simplified = Column(String)
    auth_name = Column(String)
    auth_token = Column(String)
    auth_email = Column(String)
    auth_mask = Column(String)
    auth_pass = Column(String)
    session_token = Column(String)
    points = Column(Integer)
    races = Column(Integer)
    maps = Column(Integer)
    diff_points = Column(Integer)
    awardval = Column(Integer)
    playtime = Column(BigInteger)
    created = Column(DateTime)

    def __repr__(self):
        return '<Player(id={}, name="{}")>'.format(self.id, self.simplified)


class Map(_Base):
    __tablename__ = 'map'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    longname = Column(String)
    file = Column(String)
    oneliner = Column(String)
    pj_oneliner = Column(String)
    mapper_id = Column(Integer, ForeignKey('player.id'))
    freestyle = Column(Boolean)
    status = Column(Enum(*_map_status_choices))
    races = Column(Integer)
    playtime = Column(BigInteger)
    rating = Column(Float)
    ratings = Column(Integer)
    downlaods = Column(Integer)
    force_recompution = Column(Enum(*_enum_bool))
    weapons = Column(String)
    created = Column(DateTime)

    mapper = relationship(Player)

    def __repr__(self):
        return '<Map(id={}, name="{}")>'.format(self.id, self.name)


class GameServer(_Base):
    __tablename__ = 'gameserver'

    id = Column(Integer, primary_key=True)
    user = Column(String)
    servername = Column(String)
    admin = Column(String)
    playtime = Column(BigInteger)
    races = Column(Integer)
    maps = Column(Integer)
    created = Column(DateTime)

    def __repr__(self):
        return '<GameServer(id={}, name={})>'.format(self.id, self.servername)


class Checkpoint(_Base):
    __tablename__ = 'checkpoint'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    map_id = Column(Integer, ForeignKey('map.id'))
    num = Column(Integer)
    time = Column(Integer)

    player = relationship(Player)
    map = relationship(Map)

    def __repr__(self):
        return '<Checkpoint(id={})>'.format(self.id)


class PlayerHistory(_Base):
    __tablename__ = 'player_history'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    date = Column(Date)
    points = Column(Integer)
    races = Column(Integer)
    maps = Column(Integer)
    skill = Column(Float)
    awardval = Column(Integer)
    playtime = Column(BigInteger)
    created = Column(DateTime)

    player = relationship(Player)

    def __repr__(self):
        return '<PlayerHistory(id={}, player_id={})>'.format(self.id,
                                                             self.player_id)


class PlayerMap(_Base):
    __tablename__ = 'player_map'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    map_id = Column(Integer, ForeignKey('map.id'))
    server_id = Column(Integer, ForeignKey('gameserver.id'))
    time = Column(Integer)
    races = Column(Integer)
    points = Column(Integer)
    playtime = Column(BigInteger)
    tries = Column(Integer)
    duration = Column(BigInteger)
    overall_tries = Column(Integer)
    racing_time = Column(BigInteger)
    created = Column(DateTime)
    prejumped = Column(Enum(*_enum_bool))

    player = relationship(Player)
    map = relationship(Map)
    server = relationship(GameServer)

    def __repr__(self):
        return '<PlayerMap(id={}, player_id={}, map_id={})>'.format(
               self.id, self.player_id, self.map_id)


class Race(_Base):
    __tablename__ = 'race'

    id = Column(Integer, primary_key=True)
    map_id = Column(Integer, ForeignKey('map.id'))
    player_id = Column(Integer, ForeignKey('player.id'))
    nick_id = Column(Integer)
    server_id = Column(Integer, ForeignKey('gameserver.id'))
    time = Column(Integer)
    tries = Column(Integer)
    duration = Column(BigInteger)
    created = Column(DateTime)
    prejumped = Column(Enum(*_enum_bool))

    player = relationship(Player)
    map = relationship(Map)
    server = relationship(GameServer)

    def __repr__(self):
        return '<Race(id={})>'.format(self.id)
