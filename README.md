# How to sink data from Confluent Cloud to Neo4j

The Neo4j connector isn't included in the Kafka Connect Docker image. In fact, none of the connectors are. This is done to keep the Docker Kafka Connect instance lightweight.

The first step is to create a custom Docker Kafka Connect image that contains the Neo4j connector. We do this by creating a Dockerfile containing a reference to the base image and a command to install the Neo4j connector:

    FROM confluentinc/cp-kafka-connect:6.1.1
    RUN confluent-hub install --no-prompt neo4j/kafka-connect-neo4j:1.0.9

The instance was based on the [confluentinc/cp-kafka-connect](https://hub.docker.com/r/confluentinc/cp-kafka-connect) image. For more details, read [Confluent extending images](https://docs.confluent.io/platform/current/installation/docker/development.html#extending-images) docs.

We can then build the instance:

    docker build . -t ccloud-neo4j:1.0.0

We then login to Confluent Cloud, create a cluster, generate API key(s), and get the connection properties. This can be done via the UI or CLI. Once the cluster has been created we create three (compacted) topics that will be used by Connect:

  - `connect-configs`
  - `connect-offsets`
  - `connect-status`

We can now spin-up the Kafka Connect container that contains the Neo4j sink:

    docker run -d \
      --name=kafka-connect \
      -p 8083:8083 \
      -e CONNECT_BOOTSTRAP_SERVERS="pkc-lgk0v.us-west1.gcp.confluent.cloud:9092" \
      -e CONNECT_GROUP_ID="ccloud-docker-connect" \
      -e CONNECT_CONFIG_STORAGE_TOPIC="connect-config" \
      -e CONNECT_OFFSET_STORAGE_TOPIC="connect-offsets" \
      -e CONNECT_STATUS_STORAGE_TOPIC="connect-status" \
      -e CONNECT_KEY_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
      -e CONNECT_VALUE_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
      -e CONNECT_INTERNAL_KEY_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
      -e CONNECT_INTERNAL_VALUE_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
      -e CONNECT_REST_ADVERTISED_HOST_NAME="localhost" \
      -e CONNECT_PLUGIN_PATH=/usr/share/confluent-hub-components \
      -e CONNECT_REST_PORT=8083 \
      -e CONNECT_REST_ADVERTISED_HOST_NAME="localhost" \
      -e CONNECT_SSL_ENDPOINT_IDENTIFICATION_ALGORITHM="https" \
      -e CONNECT_SASL_MECHANISM="PLAIN" \
      -e CONNECT_REQUEST_TIMEOUT_MS="20000" \
      -e CONNECT_RETRY_BACKOFF_MS="500" \
      -e CONNECT_SECURITY_PROTOCOL="SASL_SSL" \
      -e CONNECT_CONSUMER_SSL_ENDPOINT_IDENTIFICATION_ALGORITHM="https" \
      -e CONNECT_CONSUMER_SASL_MECHANISM="PLAIN" \
      -e CONNECT_CONSUMER_REQUEST_TIMEOUT_MS="20000" \
      -e CONNECT_CONSUMER_RETRY_BACKOFF_MS="500" \
      -e CONNECT_CONSUMER_SECURITY_PROTOCOL="SASL_SSL" \
      -e CONNECT_SASL_JAAS_CONFIG="org.apache.kafka.common.security.plain.PlainLoginModule required username=\"5ZR7JIDVI2N2Q5J3\" password=\"OnM75g61oRERtxnKE/7CVV44VwzPAMwI+Cb+bMYC1Tx0wIsL2IYEl4vM5d******\";" \
      -e CONNECT_CONSUMER_SASL_JAAS_CONFIG="org.apache.kafka.common.security.plain.PlainLoginModule required username=\"5ZR7JIDVI2N2Q5J3\" password=\"OnM75g61oRERtxnKE/7CVV44VwzPAMwI+Cb+bMYC1Tx0wIsL2IYEl4vM5d******\";" \
      -e CONNECT_CONNECTOR_CLIENT_CONFIG_OVERRIDE_POLICY="All" \
      -e CONNECT_LOG4J_ROOT_LOGLEVEL=INFO \
      ccloud-neo4j:1.0.0

As you can see, there are quite a few properties. At the very least, it'll be necessary to change the `BOOTSTRAP_SERVERS`, and the API key/secret in `SASL_JAAS_CONFIG` and `CONNECT_CONSUMER_SASL_JAAS_CONFIG`. For a more detailed descriptions of the properties, take a look at the [Kafka Connect long configuration](https://docs.confluent.io/platform/current/installation/docker/config-reference.html#kconnect-long-configuration) docs.

Once Dockerized Kafka Connect instance is running, we can deploy the Neo4j sink connector:

    http PUT localhost:8083/connectors/kafkaexample-neo4j/config <<< '
    {
        "connector.class": "streams.kafka.connect.sink.Neo4jSinkConnector",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "name": "kafkaexample-neo4j",
        "neo4j.database": "kafkaexample",
        "neo4j.authentication.basic.password": "V1ctoria",
        "neo4j.authentication.basic.username": "neo4j",
        "neo4j.server.uri": "bolt://neo4j.woolford.io:7687",
        "neo4j.topic.cypher.pageview": "MERGE(u:User {user: event.user}) MERGE(p:Page {page: event.page}) MERGE(u)-[:VIEWED]->(p)",
        "topics": "pageview",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": "false"
    }'

Note the templated Cypher statement. This connector will take messages, as they're produced, and write them to a Neo4j database by injecting the values from the messages into the Cypher statement. 
