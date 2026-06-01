#!/usr/bin/env bash
# Deprecated: use create_master_scaffold.sh or `hermes master init`
exec "$(dirname "$0")/create_master_scaffold.sh" "$@"
