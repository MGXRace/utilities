"""
rs_utils_old

Utility functions for managing the pre-1.1 racesow database
"""
import os
import rs_models_old as models
from sqlalchemy import create_engine
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
    for n, record in enumerate(records):

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
