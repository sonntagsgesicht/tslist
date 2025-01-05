# -*- coding: utf-8 -*-

# tslist
# ------
# timestamp with a list (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1.2, copyright Friday, 11 October 2024
# Website:  https://github.com/sonntagsgesicht/tslist
# License:  Apache License 2.0 (see LICENSE file)


import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

__doc__ = 'timestamp with a list (created by auxilium)'
__license__ = 'Apache License 2.0'

__author__ = 'sonntagsgesicht'
__email__ = 'sonntagsgesicht@icloud.com'
__url__ = 'https://github.com/sonntagsgesicht/tslist'

__date__ = 'Sunday, 05 January 2025'
__version__ = '0.3.1'
__dev_status__ = '3 - Alpha'  # '4 - Beta'  or '5 - Production/Stable'

__dependencies__ = ()
__dependency_links__ = ()
__data__ = ()
__scripts__ = ()
__theme__ = ''

# todo:
#  [ ] add tests and docs
#  [ ] add TSDiff(years=1)
#  [ ] add str operations TS() + '2d'
#  [ ] add TSDiff.from_float(t, origin=None) like 'yieldcurves.inverse'


from .ts import TS  # noqa F401 E402
from .tsdiff import TSDiff  # noqa F401 E402
from .tsobj import TSObject  # noqa F401 E402
from .tslist import TSList  # noqa F401 E402
from .tsdict import TSDict  # noqa F401 E402
from .tsdir import TSDir, NOW  # noqa F401 E402
