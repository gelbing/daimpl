#!/bin/bash
# Set number of clients
num_clients=${1:-2}

echo "Starting $num_clients clients..."
# Check if the network exists
network_exists=$(docker network ls | grep daimpl-network | wc -l)

# Create the network if it does not exist
if [ $network_exists -eq 0 ]; then
    echo "Creating network: daimpl-network"
    docker network create daimpl-network
fi


###########################################################################
# Start the server 
echo "Starting server..."
cd server
NUM_CLIENTS=${num_clients} docker-compose up --build -d --force-recreate

echo "Waiting for Server Debezium connector to start..."
while true; do
    response=$(curl --write-out '%{http_code}' --silent --output /dev/null http://localhost:7000/connectors/)
    if [ "$response" -eq 200 ]; then
        break
    else
        echo "Server Debezium connector not ready, retrying in 5 seconds..."
        sleep 5
    fi
done

# Register the servers's Debezium connector
echo "Registering Server Debezium connector..."
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:7000/connectors/ -d @register-postgres.json

###########################################################################
# Wait for Kafka
echo "Waiting for Kafka to start..."
while true; do
    response=$(docker-compose -f docker-compose.yml exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list || echo "fail")
    if [ "$response" != "fail" ]; then
        break
    else
        echo "Kafka not ready, retrying in 5 seconds..."
        sleep 5
    fi
done
# Kafka Ready
###########################################################################

###########################################################################
# Start the clients
echo "Starting $num_clients clients..."
cd ../db_client
declare -a BACKEND_PORTS=()
declare -a BACKEND_HOSTS=()
declare -a CLIENT_TOPICS=()

for i in $(seq 1 $num_clients)
do
    CLIENT_NAME="client-$i"
    DB_PORT=$((5431+i))
    CONNECTOR_PORT=$((8082+i))
    BACKEND_PORT=$((7999+i))
    BACKEND_PORTS+=(${BACKEND_PORT})
    BACKEND_HOSTS+=(${CLIENT_NAME}-backend)
    CLIENT_TOPICS+=(${CLIENT_NAME}-topic.public.todos)
    # create a custom docker-compose-$i. for each client
  cat << EOF > docker-compose-$i.yml
version: '3'
services:
  ${CLIENT_NAME}-postgres:
    container_name: ${CLIENT_NAME}-postgres
    image: quay.io/debezium/postgres:13
    ports:
      - ${DB_PORT}:5432
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - daimpl-network
  ${CLIENT_NAME}-connect:
    container_name: ${CLIENT_NAME}-connect
    image: quay.io/debezium/connect:2.3
    ports:
      - "${CONNECTOR_PORT}:8083"
    depends_on:
      - ${CLIENT_NAME}-postgres
    environment:
      - BOOTSTRAP_SERVERS=kafka:9092
      - CONFIG_STORAGE_TOPIC=my_connect_configs
      - OFFSET_STORAGE_TOPIC=my_connect_offsets
      - STATUS_STORAGE_TOPIC=my_connect_statuses
    networks:
      - daimpl-network
  ${CLIENT_NAME}-backend:
    container_name: ${CLIENT_NAME}-backend
    build:
      context: ./backend
      dockerfile: Dockerfile
    volumes:
      - ./backend:/app
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_HOST=${CLIENT_NAME}-postgres
      - POSTGRES_PORT=5432
      - CLIENT_ID=${CLIENT_NAME}
    ports:
      - ${BACKEND_PORT}:8000
    depends_on:
      - ${CLIENT_NAME}-postgres
    networks:
      - daimpl-network

networks:
    daimpl-network:
        external: true
EOF
    
    # create a custom register-postgres.json for each client
    cat << EOF > register-postgres-$i.json
{
    "name": "${CLIENT_NAME}-connector",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "tasks.max": "1",
        "database.hostname": "${CLIENT_NAME}-postgres",
        "plugin.name": "decoderbufs",
        "database.port": "5432",
        "database.user": "postgres",
        "database.password": "postgres",
        "database.dbname" : "postgres",
        "topic.prefix": "${CLIENT_NAME}-topic",
        "schema.include.list": "public"
    }
}
EOF
    # start the client
    docker-compose -f docker-compose-$i.yml up --build -d 
    
    # Wait for the Debezium connector to start before we can register it 
    echo "Waiting for Debezium connector to start..."
    while true; do
        response=$(curl --write-out '%{http_code}' --silent --output /dev/null http://localhost:${CONNECTOR_PORT}/connectors/)
        if [ "$response" -eq 200 ]; then
            break
        else
            echo "Debezium connector not ready, retrying in 5 seconds..."
            sleep 5
        fi
    done
    
    # Register the client's Debezium connector
    echo "Registering Debezium connector..."
    curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:${CONNECTOR_PORT}/connectors/ -d @register-postgres-$i.json
done
# Clients started
###########################################################################

# Convert the array of backend ports to a comma-separated string
BACKEND_PORTS_STR=$(IFS=','; echo "${BACKEND_PORTS[*]}")
BACKEND_HOSTS_STR=$(IFS=','; echo "${BACKEND_HOSTS[*]}")

###########################################################################
# Start the Streamlit Application
echo "Starting Streamlit Application..."
cd ../streamlit
docker build  .
BACKEND_HOSTS=${BACKEND_HOSTS_STR} docker-compose up -d