#!/bin/bash

TOTAL_CPUS=16
NUM_INSTANCES=2
CPUS_PER_BOT=$(( TOTAL_CPUS / NUM_INSTANCES ))

# Create logs directory if it doesn't exist
mkdir -p logs

# Clean up any existing containers
echo "Cleaning up any existing containers..."
docker ps -a | grep "bot_" | awk '{print $1}' | xargs -r docker rm -f

# Function to start a bot instance
start_bot() {
    local instance_num=$1
    docker run -d \
        --init \
        --cpus=$CPUS_PER_BOT \
        -e CPUS_PER_BOT=$CPUS_PER_BOT \
        --env-file env_$instance_num \
        --mount type=bind,source="$(pwd)"/logs,target=/foul-play/logs \
        --name "bot_${instance_num}_$(date +%s)" \
        foul-play:latest
}

# Launch all instances
declare -a containers
for i in $(seq 1 $NUM_INSTANCES); do
    container_id=$(start_bot $i)
    containers+=("$container_id")
    echo "Started bot instance $i with $CPUS_PER_BOT CPUs (Container ID: $container_id)"
    sleep 2
done

# Monitor containers
echo "Monitoring containers..."
while true; do
    active_containers=0
    for container_id in "${containers[@]}"; do
        status=$(docker inspect -f '{{.State.Status}}' "$container_id" 2>/dev/null)
        if [ "$status" = "running" ]; then
            active_containers=$((active_containers + 1))
            echo "Status for container $container_id:"
            docker logs --tail 5 "$container_id" 2>/dev/null || echo "No recent logs"
        fi
    done

    if [ $active_containers -eq 0 ]; then
        echo "All containers have finished. Exiting..."
        break
    fi

    echo "Active containers: $active_containers"
    echo "----------------------------------------"
    sleep 30
done
