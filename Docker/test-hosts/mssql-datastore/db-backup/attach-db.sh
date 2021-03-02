sleep 15s

/opt/mssql-tools/bin/sqlcmd -S . -U sa -P Testing1122 \
-Q "CREATE DATABASE [telemDataStore] ON (FILENAME = '/var/opt/sqlserver/telemDataStore.mdf'),(FILENAME = '/var/opt/sqlserver/telemDataStore_log.ldf') FOR ATTACH"