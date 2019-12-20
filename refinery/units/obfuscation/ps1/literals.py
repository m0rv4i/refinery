#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from .. import Deobfuscator, outside
from ....lib.patterns import formats


class deob_ps1_literals(Deobfuscator):
    """
    PowerShell deobfuscation that removes superfluous curly braces around
    literals that do not require it, i.e. `${variable}` is transformed to
    just `$variable`.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._sentinel = re.compile(R'\$\{(\w+)\}')

    @outside(formats.ps1str)
    def deobfuscate(self, data):
        return self._sentinel.sub(R'$\1', data)
