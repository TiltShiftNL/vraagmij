from .base import *

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DEFAULT_FILE_STORAGE = 'swift.storage.SwiftStorage'
SWIFT_CONTAINER_NAME = 'media'

THUMBNAIL_DEFAULT_STORAGE = 'swift.storage.SwiftStorage'