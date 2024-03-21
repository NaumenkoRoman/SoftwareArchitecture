@echo off
set HOST=host.docker.internal
set PORT=%1
set NAME=%2
docker run --name %NAME% --network hazelcast-network --rm -e HZ_QUEUE_QUEUE_MAXSIZE=10 -e HZ_NETWORK_PUBLICADDRESS=%HOST%:%PORT% -e HZ_CLUSTERNAME=hello-world -p %PORT%:5701 hazelcast/hazelcast:5.3.6