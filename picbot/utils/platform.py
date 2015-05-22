
import unicodedata
import re
import os
import platform

is_mac = platform.system() == 'Darwin'
is_windows = platform.system() == 'Windows'
is_linux = platform.system() == 'Linux'


FILESYSTEM_INVALID_CHARS = re.compile(r'[\\/:*?"<>|]')


def normalize_filename(expr, replace_to='_'):
    replaced_expr = FILESYSTEM_INVALID_CHARS.sub(replace_to, expr)
    if is_mac:
        # TODO: Mac(HFS+)'s unicode normalization does not conform to Unicode NFD
        return unicodedata.normalize('NFD', replaced_expr)
    else:
        return unicodedata.normalize('NFC', replaced_expr)


def absjoin(*args):
    return os.path.abspath(os.path.join(*args))


APP_ROOT = absjoin(os.path.dirname(__file__), '../../')


def app_path(*args):
    if os.path.isabs(os.path.join(*args)):
        return os.path.join(*args)
    else:
        return absjoin(APP_ROOT, *args)

