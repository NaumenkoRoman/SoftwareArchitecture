#!/bin/bash
echo off
echo "Starting Consul Server"
docker-compose up -d consul
echo "Waiting for Consul Server to start"
sleep 5

echo "Setting configuration in Consul Server"
docker exec -it consul-server consul kv put rabbitmq/host "rabbitmq"
docker exec -it consul-server consul kv put rabbitmq/queue "message_queue"

docker exec -it consul-server consul kv put hazelcast/logging_service1 "hazelcast1"
docker exec -it consul-server consul kv put hazelcast/logging_service2 "hazelcast2"
docker exec -it consul-server consul kv put hazelcast/logging_service3 "hazelcast3"

docker exec -it consul-server consul kv put hazelcast/port "5701"
docker exec -it consul-server consul kv put hazelcast/map_name "distributed-map"
