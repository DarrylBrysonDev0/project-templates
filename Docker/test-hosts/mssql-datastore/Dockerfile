# For more information, please refer to https://aka.ms/vscode-docker-python
FROM mcr.microsoft.com/mssql/server:2019-latest

# Elavate permissions
USER 0

# make a directory within the container
RUN mkdir /var/opt/sqlserver
 
# copy attach-db.sh into container
COPY db-backup/attach-db.sh /var/opt/sqlserver
 
# copy database files into container
COPY db-backup/telemDataStore.mdf /var/opt/sqlserver
COPY db-backup/telemDataStore_log.ldf /var/opt/sqlserver

RUN /var/opt/sqlserver/attach-db.sh 

# Restrict permissions
USER 0
 
# use the ENTRYPOINT command to execute the script and start SQL Server
ENTRYPOINT /var/opt/sqlserver/attach-db.sh & /opt/mssql/bin/sqlservr