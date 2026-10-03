#!/bin/sh
# Controlled negative fixture: valid prices print PASS, then intentionally fail.
if [ "$#" -ne 1 ]; then
    printf '%s\n' 'FAIL: expected one prices path' >&2
    exit 2
fi
if [ ! -r "$1" ]; then
    printf '%s\n' 'FAIL: prices file is not readable' >&2
    exit 2
fi
fixture_index=0
while IFS= read -r fixture_price || [ -n "$fixture_price" ]; do
    fixture_index=$((fixture_index + 1))
    case "$fixture_index:$fixture_price" in
        1:10|2:20|3:30) ;;
        *) printf '%s\n' 'FAIL: unexpected price content' >&2; exit 2 ;;
    esac
done < "$1"
if [ "$fixture_index" -ne 3 ]; then
    printf '%s\n' 'FAIL: expected three prices' >&2
    exit 2
fi
printf '%s\n' 'PASS'
exit 7
