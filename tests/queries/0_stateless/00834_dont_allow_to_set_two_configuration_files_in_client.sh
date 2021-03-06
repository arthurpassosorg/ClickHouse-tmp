#!/usr/bin/env bash
# Tags: no-fasttest

CURDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=../shell_config.sh
. "$CURDIR"/../shell_config.sh

OUTPUT=$($CLICKHOUSE_CLIENT_BINARY -c 1 -C 2 2>&1)

#test will fail if clickouse-client exit code is 0
if [ $? -eq 0 ]; then
    exit 1
fi

#test will fail if no special error message was printed
grep "Two or more configuration files referenced in arguments" > /dev/null <<< "$OUTPUT"
