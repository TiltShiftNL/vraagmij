from .base import *

# CRONJOBS = [
#     ('*/5 * * * *', 'jeugdzorg.cron.update_regeling_bron_job')
# ]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DEFAULT_FILE_STORAGE = 'swift.storage.SwiftStorage'
SWIFT_CONTAINER_NAME = 'media'

THUMBNAIL_DEFAULT_STORAGE = 'swift.storage.SwiftStorage'

# DEBUG = False