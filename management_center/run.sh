#!/bin/bash

docker build -t hazelcast-management-center .

if [ $(docker ps -aq -f name=hazelcast-management-center) ]; then
   docker stop hazelcast-management-center
   docker rm hazelcast-management-center
fi

docker run -d --name hazelcast-management-center --network=hazelcast-net -p 8080:8080 hazelcast-management-center
