# project-templates

## Setup Instructions
1. Create test docker network
```bash
    docker network create microservice-network
```
2. Deploy shared hosting services
```bash
    docker-compose -f "Docker/test-hosts/docker-compose.test-interface-hosts.yml" -d --build
```
3. 
