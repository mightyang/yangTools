#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : plugins__init__.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 05.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import os

__all__ = []
contents = os.listdir('.')
for content in contents:
    if os.path.isdir(content):
        __all__.append(content)
