#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : __init__.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 10.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import os

__all__ = []
pwd = os.path.dirname(os.path.abspath(__file__))
contents = os.listdir(pwd)
for content in contents:
    if os.path.isdir(os.path.join(pwd, content)):
        __all__.append(content)

from . import *

print '-----------------------------------'
