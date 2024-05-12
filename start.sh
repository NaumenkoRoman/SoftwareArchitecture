#!/bin/bash
!echo off
echo "Starting Consul Server"
docker-compose up -d consul
echo "Waiting for Consul Server to start"
sleep 5

echo "Setting configuration in Consul Server"
docker exec -it consul-server consul kv put rabbitmq/host "rabbitmq"
docker exec -it consul-server consul kv put rabbitmq/queue "message_queue"
docker exec -it consul-server consul kv put hazelcast/config "default_config"

echo "Starting the rest of the services"
docker-compose up -d
