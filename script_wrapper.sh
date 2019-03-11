#!/bin/bash

set -m

python ./consume_events.py &
python ./generate_events.py &
cron -f && tail /var/log/upload.log

fg %1
