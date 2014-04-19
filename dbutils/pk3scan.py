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
import sys
from zipfile import ZipFile
from pathlib import Path, PurePath
from docopt import docopt


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
    pass


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
