# encoding: utf-8
#----------------------------------------
# file.py by Thomas Gläßle
# 
# To the extent possible under law, the person who associated CC0 with
# file.py has waived all copyright and related or neighboring rights
# to file.py.
# 
# You should have received a copy of the CC0 legalcode along with this
# work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#----------------------------------------
"""
Resource provider for plain filesystem resources.
"""
__all__ = ['FileResource']

import os
from io import open
from contextlib import contextmanager

from .base import ResourceProvider

class FileResource(ResourceProvider):
    """
    File system resource provider.

    Uses the builtins open() to open ordinary files and os.listdir() to list
    directory contents.

    """
    def __init__(self, path):
        """
        Initialize the filesystem resource provider.

        :param string path: name of a filesystem object (file/folder).

        """
        self.path = path

    def open(self, name='', encoding=None):
        if encoding is None:
            return open(self._get_path(name), 'rb')
        else:
            return open(self._get_path(name), 'rt', encoding=encoding)

    def listdir(self, name=''):
        return os.listdir(self._get_path(name))

    def get(self, name=''):
        return self.__class__(self._get_path(name))

    @contextmanager
    def filename(self, name=''):
        yield self._get_path(name)

    def _get_path(self, name):
        if not name:
            return self.path
        elif isinstance(name, list):
            return os.path.join(self.path, *name)
        else:
            return os.path.join(self.path, *name.split('/'))

    def provider(self):
        return self.__class__(os.path.dirname(self.path))

