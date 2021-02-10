---
title: "microservice-interface-class-information"
date: 2021-02-08T10:00:00
categories:
  - Readme
tags:
  - library
  - python
  - docker
excerpt: "Summary information of interface classes for container solutions"
---
# Microservice Interface Class Summarry
## Overview
Summary information of interface classes for container solutions.

## sftp_CONN
Class wrapper for pysftp library. Implementation of sftp server client interface logic for file access.

- Connection managment
  - get_conn
  - close_conn
- Directory managment
  - get_dir_list
  - path_exists
  - create_directory
- File managment
  - download_file
  - upload_sftp
  - delete_sftp
  - append_sftp
- State managment
  - from_env
  - to_list
  - set_env_param

## queue_CONN
Class wrapper for pika library. Implementation of RabbitMQ interface logic for intra-container/task messaging.
- Connection manager
  - create connections
  - create channels
  - create queues
  - close connections
- Queue communication
  - create publisher
  - create consumer
- input connection
  - input channel
- output connection
  - output channel
  - namespace channel
- State managment
  - from_env
  - to_list
  - set_env_param
