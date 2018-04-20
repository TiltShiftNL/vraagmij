#!/bin/sh
export TZ="Europe/Amsterdam"
export CRON_TZ="Europe/Amsterdam"
/usr/local/bin/python /opt/app/manage.py mail_account_active_check