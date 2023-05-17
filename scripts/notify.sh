#!/bin/bash

STATUS="$1"
MESSAGE="$2"
DETAILS="$3"
SLACK_URL="$4"

if [[ -z $STATUS || -z $MESSAGE || -z $DETAILS || -z $SLACK_URL ]]; then
    echo "Missing required parameter!"
    echo "Usage: notify.sh <<STATUS>> <<MESSAGE>> <<DETAILS>> <<SLACK_URL>>"
    exit 1
fi

data=$(printf '{"text": "%s", "attachments": [{"text": "%s", "color": "%s"}]}' "$MESSAGE" "$DETAILS" "$STATUS")
curl -XPOST -H "Content-Type: application/json" -d "$data" "$SLACK_URL"
