#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : scriptsytLoggingSettings.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 06.03.2019
# Last Modified Date: 14.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(asctime)s %(thread)d %(filename)s %(funcName)s[%(lineno)d]: %(message)s')
yl = logging.getLogger('yangTools')
