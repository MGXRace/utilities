"""
pk3scan

Usage:
    pk3scan.py scan <pk3dir> <basedir>
    pk3scan.py update <pk3dir>

Scans a folder for pk3 files and checks them for the following:
    File and shader conflicts with those in basedir
    Repeated textures packs

"""
import logging
import os
import re
import sys
from rs_models import Map, Tag
from docopt import docopt
from pathlib import Path
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from zipfile import ZipFile


# Configure the db connection
_engine = create_engine(os.getenv('PK3SCANDB'))
_session = sessionmaker()
_session.configure(bind=_engine)
session = _session()


# A dict mapping entity classnames to a maptag
_TAGMAP = {
    # 'weapon_grapplinghook', 'gh',
    'weapon_gauntlet': 'gb',
    'weapon_gunblade': 'gb',
    'weapon_machinegun': 'eb',
    'weapon_rocketlauncher': 'rl',
    'weapon_plasmagun': 'pg',
    'weapon_shotgun': 'rg',
    'weapon_riotgun': 'rg',
    'weapon_grenadelauncher': 'gl',
    'weapon_lightning': 'lg',
    'weapon_electrobolt': 'eb',
    'weapon_railgun': 'eb',
    'weapon_bfg': 'pg',
    'weapon_instagun': 'ig'
}

def get_or_create(obj, flt):
    """
    Get or create the tag with a given name

    Args:
        obj - The Model object or table to get from
        flt - a kwarg dict to pass to filter_by or create the object with

    Returns:
        A tuple of (instance, created)
    """
    result = session.query(obj).filter_by(**flt).first()
    found = False

    if not result:
        result = obj(**flt)
        found = True
        session.add(result)

    return result, found

def parse_shader(shader):
    """
    Create an index of files defined by the shader

    Args:
        shader - a file-like object to the shader

    Returns:
        A set of filenames provided by the shader
    """
    result = set()

    for line in shader:
        line = line.decode('utf-8', 'ignore').strip()
        if line.endswith('/') or not line.startswith('textures'):
            continue

        result.add(line)

    return result


def parse_bsp(bspfile, mapobj):
    """
    Add a map to the database and tag it according to entities on the map

    Args:
        bspfile - The bspfile of the map
        mapobj - Instance of the map model to update
    """
    logger = logging.getLogger('parse_bsp')
    tags = set()
    weaponre = re.compile(r'\"classname\" \"(weapon_[a-z]*)\"',
        flags=re.IGNORECASE)

    for line in bspfile:
        line = line.decode('ascii', 'ignore').strip()
        matches = weaponre.findall(line)
        if matches:
            for match in matches:
                if not match in _TAGMAP:
                    logger.info('Unknown weapon: {}'.format(match))
                    continue
                tag, created = get_or_create(Tag, {'name': _TAGMAP[match]})
                tags.add(tag)
    return tags


def scan(pk3dir, basedir):
    """
    Scan a pk3 files in a folder

    Check for shader conflicts and build a report of texture usages.

    Args:
        pk3dir - Path to a directory containing pk3 files to scan
        basedir - Path to directory of a clean game installation (basewsw)
    """
    logger = logging.getLogger('scan')
    pk3path = Path(pk3dir)
    basepath = Path(basedir)

    if not pk3path.is_dir():
        logger.error('{} is not a valid directory'.format(pk3path))
        sys.exit(1)

    if not basepath.is_dir():
        logger.error('{} is not a valid directory'.format(basepath))
        sys.exit(1)

    # Build an index of base game files to check against
    basefiles = set()
    for pk3file in basepath.glob('*.pk3'):
        pk3zip = ZipFile(str(pk3file))
        for name in pk3zip.namelist():
            if name.endswith('/'):
                continue
            elif name.endswith('.shader'):
                basefiles.update(parse_shader(pk3zip.open(name)))
            else:
                basefiles.add(name)

    # Check if pk3s include same files
    for pk3file in pk3path.glob('*.pk3'):
        pk3zip = ZipFile(str(pk3file))
        for name in pk3zip.namelist():
            if name in basefiles:
                logging.error('{} overwrites file {}'.format(pk3file, name))

            if name.endswith('.shader'):
                for texture in basefiles & parse_shader(pk3zip.open(name)):
                    logging.error('{} overwrites file {}' \
                                    .format(pk3file, texture))


def update(pk3dir):
    """
    Update the database with map information parsed from pk3 files in folder

    Args:
        pk3dir - Path to a directory containing pk3 files to scan and update
    """
    logger = logging.getLogger('update')
    pk3path = Path(pk3dir)

    if not pk3path.is_dir():
        logger.error('{} is not a valid directory'.format(pk3path))
        sys.exit(1)

    for pk3file in pk3path.glob('*.pk3'):
        pk3zip = ZipFile(str(pk3file))
        mapfiles = [x for x in pk3zip.namelist() if x.endswith('.bsp')]

        if not mapfiles:
            logger.info('pk3 {} contains no maps, skipping'.format(pk3file))
            continue

        for mapfile in mapfiles:
            logger.debug('Parsing bsp: {}'.format(mapfile))
            mapobj, created = get_or_create(Map, {'name': mapfile[5:-4]})
            if not created:
                continue

            tags = parse_bsp(pk3zip.open(mapfile), None)
            if not tags:
                tag, created = get_or_create(Tag, {'name': 'strafe'})
                tags.add(tag)

            mapobj.pk3file = str(pk3file)
            mapobj.tags.extend(tags)
            session.commit()
            logger.info('Added map {} with tags: {}'.format(mapfile[5:-4], tags))


def main():
    """Utilities Main method"""
    args = docopt(__doc__)
    if args['scan']:
        scan(args['<pk3dir>'], args['<basedir>'])
    else:
        update(args['<pk3dir>'])

if __name__ == '__main__':
    logging.basicConfig(filename='pk3scan.log', level=logging.DEBUG)
    _CONLOG = logging.StreamHandler()
    _CONLOG.setLevel(logging.INFO)
    logging.getLogger('').addHandler(_CONLOG)
    main()
