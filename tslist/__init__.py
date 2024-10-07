# -*- coding: utf-8 -*-

# tslist
# ------
# timestamp with a list (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1, copyright Monday, 07 October 2024
# Website:  https://github.com/sonntagsgesicht/tslist
# License:  Apache License 2.0 (see LICENSE file)


import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

__doc__ = 'timestamp with a list (created by auxilium)'
__license__ = 'Apache License 2.0'

__author__ = 'sonntagsgesicht'
__email__ = 'sonntagsgesicht@icloud.com'
__url__ = 'https://github.com/sonntagsgesicht/tslist'

__date__ = 'Monday, 07 October 2024'
__version__ = '0.1'
__dev_status__ = '3 - Alpha'  # '4 - Beta'  or '5 - Production/Stable'

__dependencies__ = ()
__dependency_links__ = ()
__data__ = ()
__scripts__ = ()
__theme__ = ''


from .tslist import ts, TS, TSList
