from .base import *

# CRONJOBS = [
#     ('*/5 * * * *', 'jeugdzorg.cron.update_regeling_bron_job')
# ]

DEFAULT_FILE_STORAGE = 'swift.storage.SwiftStorage'
SWIFT_CONTAINER_NAME = 'media'

DEBUG = False