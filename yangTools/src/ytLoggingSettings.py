#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytLoggingSettings.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 06.03.2019
# Last Modified Date: 06.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s %(funcName)s[%(lineno)d] %(levelname)s: %(message)s')
yl = logging.getLogger('yangTools')
