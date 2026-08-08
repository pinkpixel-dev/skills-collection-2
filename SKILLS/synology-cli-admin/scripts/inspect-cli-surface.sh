#!/bin/sh
# Read-only Synology CLI compatibility inventory. Never invokes sudo.

set -u

printf '%s\n' 'Synology CLI surface'
printf 'Observed: %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"
printf 'Host: %s\n' "$(hostname 2>/dev/null || printf unknown)"
printf 'Kernel: %s\n' "$(uname -srmo 2>/dev/null || uname -a)"

if [ -r /etc.defaults/VERSION ]; then
    productversion="$(sed -n 's/^productversion="\([^"]*\)"/\1/p' /etc.defaults/VERSION | head -n 1)"
    buildnumber="$(sed -n 's/^buildnumber="\([^"]*\)"/\1/p' /etc.defaults/VERSION | head -n 1)"
    smallfixnumber="$(sed -n 's/^smallfixnumber="\([^"]*\)"/\1/p' /etc.defaults/VERSION | head -n 1)"
    printf 'DSM: %s build %s update %s\n' \
        "${productversion:-unknown}" "${buildnumber:-unknown}" "${smallfixnumber:-unknown}"
fi

printf '\n%-18s %-8s %-8s %s\n' 'COMMAND' 'EXISTS' 'EXEC' 'PATH'
for command_name in \
    synouser synogroup synoshare synonet synoservice synowin \
    synosystemctl synopkg
do
    command_path="$(command -v "$command_name" 2>/dev/null || true)"

    if [ -z "$command_path" ]; then
        for candidate in \
            "/usr/syno/bin/$command_name" \
            "/usr/syno/sbin/$command_name" \
            "/usr/local/bin/$command_name"
        do
            if [ -e "$candidate" ]; then
                command_path="$candidate"
                break
            fi
        done
    fi

    if [ -n "$command_path" ]; then
        if [ -x "$command_path" ]; then
            executable=yes
        else
            executable=no
        fi
        printf '%-18s %-8s %-8s %s\n' "$command_name" yes "$executable" "$command_path"
    else
        printf '%-18s %-8s %-8s %s\n' "$command_name" no no '-'
    fi
done

printf '\nNotes:\n'
printf '%s\n' '- EXEC reflects the current user, not root.'
printf '%s\n' '- Existence does not establish supported syntax.'
printf '%s\n' '- Inspect installed help and current Synology documentation before mutation.'
