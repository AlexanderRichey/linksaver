#!/bin/bash
set -e

echo "Installing repo"
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

echo "Installing binaries"
apt-get update
apt-get install -y mongodb-org

echo "Setting up default settings"
rm -rf /var/lib/mongodb/*
cat > /etc/mongod.conf <<'EOF'
# mongod.conf

# for documentation of all options, see:
#   http://docs.mongodb.org/manual/reference/configuration-options/

# Where and how to store data.
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
#  engine:
#  mmapv1:
#  wiredTiger:

# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

# network interfaces
net:
  port: 27017
  bindIp: 0.0.0.0


# how the process runs
processManagement:
  timeZoneInfo: /usr/share/zoneinfo

security:
  authorization: enabled

#operationProfiling:

#replication:

#sharding:

## Enterprise-Only Options:

#auditLog:

#snmp:

EOF

echo "Starting mongod"
systemctl start mongod

sleep 5

echo "Adding admin user"
mongo admin <<'EOF'
use admin
var user = {
  "user" : "admin",
  "pwd" : "admin",
  roles : [
      {
          "role" : "root",
          "db" : "admin"
      }
  ]
}
db.createUser(user);
exit
EOF

echo "Enabling auto start after reboot"
systemctl enable mongod

echo "Complete"

