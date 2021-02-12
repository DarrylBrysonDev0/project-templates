# python-app-loop
```bash
Project Structure:
├──────────────────────────────────
├── ./
│   └── docker-compose.python-app-loop.yml [Deployment template]
│   └── docker-compose.test-interface-hosts.yml [Example communication interface host]
│       
│── ./app-image/
│   └── requirements.txt
│   └── python-app-loop.py [Template python script]
│   └── Dockerfile.python-app-loop [Template Docker image file]
└──────────────────────────────────
```
## Quick Start
1. Create docker network 
   ```bash
    docker network create -d bridge microservice-network
   ```
2. Update source/target directory
   ```yaml
    services:
        sftp-srv:
            image: atmoz/sftp
            volumes:
                - <LOCAL/SOURCE/DIR>:/home/admin/src
                - <LOCAL/TARGET/DIR>:/home/admin/trg
   ```
   *docker-compose.test-interface-hosts.yml*
3. Deploy interface hosts
   ```bash
    docker-compose -f 'docker-compose.test-interface-hosts.yml' up -d
5. Deploy template service
   ```bash
    docker-compose -f 'docker-compose.python-app-loop.yml' up --build
   ```
## Configuration
```bash
environment variables:
├──────────────────────────────────
├── SFTP Server
│   └── SFTP_HOST
│   └── SFTP_PORT
│   └── SFTP_USR
│   └── SFTP_PWD
│       
│── Communication Queue
│   └── RABBIT_SRV
│   └── NAMESPACE
│   └── INPUT_QUEUE
│   └── OUTPUT_QUEUE
│       
│── Container Behavior
│    └── PUBLISHING_LIMIT
│    └── FREQUENCY_SEC
│       
│── File Access
│    └── SOURCE_PATH
│    └── DEST_PATH
│    └── SECONDARY_PATHS
│        └── SP_1
│        └── SP_n
└──────────────────────────────────
```
The configuration standardizes a set of input/output channels and some container behavior. Configure the Docker image using the following environment variables:

* `SFTP_HOST`: Host name or ip address for sftp interface. Default: **localhost**.
* `SFTP_PORT`: Host ssh port for sftp interface. Default: **22**.
* `SFTP_USR`: User for sftp interface. Default: **admin**.
* `SFTP_PWD`: Password for sftp interface. Default: **pwd**.
* `RABBIT_SRV`: Host name or ip address for messaging  interface. Default: **rabbit-queue**.
* `NAMESPACE`: Base name to use for reporting container status. Default: ***uuid***.
* `INPUT_QUEUE`: Queue to use as an input channel of messages. Default: **new_files**.
* `OUTPUT_QUEUE`: Queue to use as an output channel of messages. Default: **processed_files**.
* `PUBLISHING_LIMIT`: Maximum number of messages to publish to the output queue. Default: **20**.
* `FREQUENCY_SEC`: Time in sec. between restarting containers. Only effective when ```restart: unless-stopped``` flag is set. Default: **300**.
* `SOURCE_PATH`: Source SFTP directory of input files. **/src**.
* `DEST_PATH`: Output SFTP directory of result files. **/trgt**.
* `SECONDARY_PATHS`: Additional directories. Optional. Default: **admin**.