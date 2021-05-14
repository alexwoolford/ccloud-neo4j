FROM confluentinc/cp-kafka-connect:6.1.1

RUN confluent-hub install --no-prompt neo4j/kafka-connect-neo4j:1.0.9
