from .base import *

DEBUG = True

# CRONJOBS = [
#     ('*/1 * * * *', 'jeugdzorg.cron.update_regeling_bron_job', '>> /var/log/scheduled_job.log 2>&1')
# ]

del TEMPLATES[0]['OPTIONS']['loaders']
TEMPLATES[0]['APP_DIRS'] = True
TEMPLATES[0]['DIRS'] = []

MEDIA_ROOT = '/opt/file_upload/'

try:
    from .local import *
except ImportError:
    pass
