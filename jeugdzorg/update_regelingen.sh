#!/bin/sh
export TZ="Europe/Amsterdam"
export CRON_TZ="Europe/Amsterdam"
/usr/local/bin/python /opt/app/manage.py update_regeling_bron --settings jeugdzorg.settings.production