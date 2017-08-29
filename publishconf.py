#!/usr/bin/env python
# -*coding: utf-8 -*#
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'https://dl.kyleisom.net'
RELATIVE_URLS = False
FEED_DOMAIN = SITEURL
FEED_ATOM = "index.atom"
FEED_RSS = "index.rss"
DELETE_OUTPUT_DIRECTORY = True
