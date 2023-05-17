#!/bin/bash

set -e

APPROVAL_NAME="$1"

for i in {1..10}; do
  sleep 10
  
  # Get all checks for given commit
  curl -s --request GET --url "https://api.github.com/repos/$CIRCLE_PROJECT_USERNAME/$CIRCLE_PROJECT_REPONAME/statuses/$CIRCLE_SHA1" \
  --header 'Accept: application/vnd.github.v3+json' \
  --header "Authorization: Bearer $GITHUB_TOKEN" > status.json

  # Extract check names
  jq -r '.[].context' < status.json > checks.txt

  # Check for approval in commit checks
  if grep -q "ci/circleci: $CIRCLE_PROJECT_REPONAME/$APPROVAL_NAME" "checks.txt"; then
    # Get check url
    URL=$(jq -r --arg name "$CIRCLE_PROJECT_REPONAME/$APPROVAL_NAME" -c 'map(select(.context | contains($name))) | .[].target_url' < status.json | head -1)

    curl --request POST \
      --url "https://api.github.com/repos/$CIRCLE_PROJECT_USERNAME/$CIRCLE_PROJECT_REPONAME/statuses/$CIRCLE_SHA1" \
      --header 'Accept: application/vnd.github.v3+json' \
      --header "Authorization: Bearer $GITHUB_TOKEN" \
      --header 'Content-Type: application/json' \
      --data '{
        "state": "success",
        "target_url": "'"$URL"'",
        "description": "Approval marked as successful in gh, to trigger visit CircleCI",
        "context": "ci/circleci: '"$CIRCLE_PROJECT_REPONAME/$APPROVAL_NAME"'"
      }'

    exit 0
  fi
done
