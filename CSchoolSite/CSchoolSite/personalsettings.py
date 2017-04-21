# DATABASE CONFIGURATION
# options: sqlite3, postgresql, mysql
DATABASE_ENGINE = "sqlite3"

# db name / sqlite db file
DATABASE_NAME = "db.sqlite3"

DATABASE_USER = ""
DATABASE_PASSWORD = ""
DATABASE_HOST = ""
DATABASE_PORT = ""

# EJUDGE CONFIGURATION

EJUDGE_CONTEST_ID = 1
EJUDGE_USER_LOGIN = "ejudge"
EJUDGE_USER_PASSWORD = "ejudge"
EJUDGE_BIN = "/home/ejudge/inst-ejudge/bin"

# FILE SERVING CONFIGURATION
# determines how files will be returned to user 
#
# options: django, xsendfile, nginx
#
# django - django thread returns file
# xsendfile - file is returned via HTTP header X-Sendfile
# nginx - file is returned via HTTP header X-Accel-Redirect
FILESERVE_METHOD = "django"

# this option is used for X-Accel-Redirect
# mark this URL in your nginx configuration as internal
# point this URL root to MEDIA_ROOT
FILESERVE_MEDIA_URL = "/serve"

# OTHER CONFIGURATION
DEBUG = True
MEDIA_URL = "/media/"
STATIC_URL = "/static/"
