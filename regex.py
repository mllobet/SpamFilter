#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import re

pattern = "'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'"

findUrl = re.compile(pattern)
