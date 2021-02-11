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
# Microservice Interface Class Summary
## Overview
Summary information of interface classes for container solutions.

## Class: sftp_CONN
Class wrapper for pysftp library. Implementation of sftp server client interface logic for file access.

- Connection management
  - get_conn
  - close_conn
- Directory management
  - get_dir_list
  - path_exists
  - create_directory
- File management
  - download_file
  - upload_sftp
  - delete_sftp
  - append_sftp
- State management
  - from_env
  - to_list
  - set_env_param

## Class: queue_CONN
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
- State management
  - from_env
  - to_list
  - set_env_param
