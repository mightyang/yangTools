#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : menu.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 06.03.2019
# Last Modified Date: 10.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import yangTools


yt = yangTools.yangTools.yangTools()
t = nuke.toolbar('Nodes')
m = t.menu('yang')
if not m:
    m = t.addMenu('yang')
m.addCommand('yangTools', 'yt.show()')
