#!/bin/sh

echo "Starting DockerContainer..."

crond -f -l 8 -d 8 -L /dev/stdout