"""
rs_utils_old

Utility functions for managing the pre-1.1 racesow database
"""
import os
import rs_models_old as models
from collections import defaultdict
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# points for each rank
_pointmap = [40, 34, 31] + list(range(27, 0, -1))

# Configure the db connection
_RSNAME = os.getenv('RSNAME', None)
_RSPASS = os.getenv('RSPASS', None)
_RSHOST = os.getenv('RSHOST', None)
_RSDATABASE = os.getenv('RSDATABASE', None)
_engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(
    _RSNAME, _RSPASS, _RSHOST, _RSDATABASE))
_session = sessionmaker()
_session.configure(bind=_engine)
session = _session()


def recalc_map_points(mid):
    """
    Recalculate the points for each record on a map

    args:
        mid (int): ID of the map to recalculate
    """
    pm = models.PlayerMap
    records = session.query(pm).\
                      filter(pm.map_id == mid,
                             pm.time != None,
                             pm.prejumped == 'false').\
                      order_by(pm.time).all()

    rank = -1
    last_time = None
    for record in records:

        # increase rank if not tied w/ last
        if record.time != last_time:
            rank += 1

            # Break out if the race doesnt get points
            if rank >= len(_pointmap):
                break
        last_time = record.time
        record.points = _pointmap[rank]

    # Set all other records to 0 points
    session.query(pm).\
            filter(pm.map_id == mid,
                   (pm.prejumped == 'true') |
                   (pm.time == None) |
                   (pm.time > last_time)).\
            update({pm.points:0})
    session.commit()


def recalc_player_points(pid):
    """
    Recalculate the points for a player

    args:
        pid (int): ID of the player to recalculate
    """
    pm = models.PlayerMap
    player = session.query(models.Player).get(pid)
    player.points = session.query(func.sum(pm.points)).\
                            filter(pm.player_id == pid, pm.points > 0).\
                            scalar()
    session.commit()


def merge_players(pid, *alt_pids):
    """
    Merge records from multiple player entries into one.
    Ignores prejump status, so it will keep the lowest time even if that time
    is prejumped. It also deletes records which do not have a time.

    args:
        pid (int): The player id of the target account to merge into
        alt_pids (iterable): Iterable of player ids to merge
    """
    pm = models.PlayerMap
    player = session.query(models.Player).get(pid)
    print("Target player: {}\n".format(player))

    # Get the alternate players
    alt_players = session.query(models.Player).\
                          filter(models.Player.id.in_(alt_pids))


    for pid_ in alt_pids:
        found = list(filter(lambda x: x.id == pid_, alt_players))
        if not found:
            print("Player not found for id: {}".format(pid_))

    print("Merging players")
    for n, alt in enumerate(alt_players):
        print(n, alt)

    confirm = input("Is this correct [y/n]: ")
    if confirm not in ['y', 'Y']:
        return

    # Get all records for all interesting players
    records = session.query(pm).\
                      filter((pm.player_id == pid) |
                             pm.player_id.in_(alt_pids)).\
                      all()

    # Group them by map
    map_records = defaultdict(list)
    for record in records:
        map_records[record.map_id].append(record)

    # process each map
    for mid, mrecords in map_records.items():
        # find the best record
        # due to a bug in sqlalchemy, we cant use min() on filtered records
        best = None
        for rec in filter(lambda x: x.time is not None, mrecords):
            if not best or rec.time < best.time:
                best = rec

        # delete the rest
        for rec in mrecords:
            if rec is best:
                continue
            session.delete(rec)
        session.commit()

        # transfer ownership of the best rec
        if best is not None:
            best.player_id = pid

    # delete alt players
    for p in alt_players:
        session.delete(p)
    session.commit()
