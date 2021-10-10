#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from refinery.units.formats import PathExtractorUnit, UnpackResult
from refinery.units import RefineryImportMissing
from refinery.lib.structures import MemoryFile


class winreg(PathExtractorUnit):
    """
    Extract values from a Windows registry hive.
    """
    def _walk(self, key, *path):
        here = '/'.join(path)
        if not self._check_reachable(here):
            self.log_debug(F'pruning search at {here}')
            return
        for value in key.values():
            vpath = F'{here}/{value.name()}'
            yield UnpackResult(vpath, lambda v=value: v.raw_data())
        for subkey in key.subkeys():
            yield from self._walk(subkey, *path, subkey.name())

    def unpack(self, data):
        try:
            from Registry.Registry import Registry
        except ModuleNotFoundError:
            raise RefineryImportMissing('python-registry')
        with MemoryFile(data) as stream:
            root = Registry(stream).root()
            yield from self._walk(root, root.name())
