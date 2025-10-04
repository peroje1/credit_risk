#!/bin/sh
# wait-for-db.sh

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until mysql -h "$host" -P "$port" -u"risk_user" -p"StrongPass123!" --ssl=0 -e 'select 1' > /dev/null 2>&1; do
  >&2 echo "MySQL is unavailable - sleeping"
  mysql -h "$host" -P "$port" -u"risk_user" -p"StrongPass123!" --ssl=0 -e 'select 1' | echo
  sleep 2
done

>&2 echo "MySQL is up - executing command"
exec $cmd
