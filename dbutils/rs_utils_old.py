"""
rs_utils_old

Utility functions for managing the pre-1.1 racesow database
"""
import os
import rs_models_old as models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_RSNAME = os.getenv('RSNAME', None)
_RSPASS = os.getenv('RSPASS', None)
_RSHOST = os.getenv('RSHOST', None)
_RSDATABASE = os.getenv('RSDATABASE', None)
_engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(
    _RSNAME, _RSPASS, _RSHOST, _RSDATABASE))
_session = sessionmaker()
_session.configure(bind=_engine)
session = _session()
