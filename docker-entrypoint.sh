#!/bin/bash

set -e

cd /gemet && python manage.py migrate && python manage.py runserver 0.0.0.0:8000