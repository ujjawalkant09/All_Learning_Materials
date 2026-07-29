# Kafka 4.0 KRaft Cluster Setup

This project runs a 3-node Apache Kafka 4.0 cluster in KRaft mode using Docker Compose.

## Start the Cluster

Start all Kafka brokers in detached mode:

```bash
docker compose up -d
```

## Verify the Cluster

Check that all containers are running:

```bash
docker ps
```

Expected output should include:

```text
kafka1
kafka2
kafka3
```

---

## Create a Topic with Multiple Partitions

### Enter a Broker Container

```bash
docker exec -it kafka1 bash
```

### Create the Topic

```bash
/opt/kafka/bin/kafka-topics.sh \
  --create \
  --topic orders \
  --bootstrap-server localhost:9092 \
  --partitions 6 \
  --replication-factor 3
```

### Verify the Topic

```bash
/opt/kafka/bin/kafka-topics.sh \
  --describe \
  --topic orders \
  --bootstrap-server localhost:9092
```

---

# Kafka UI

Run Kafka UI on the same Docker network as the Kafka cluster:

```bash
docker run -d \
  --name kafka-ui \
  --network kafka_default \
  -p 8080:8080 \
  -e DYNAMIC_CONFIG_ENABLED=true \
  provectuslabs/kafka-ui
```

Open Kafka UI in your browser:

```text
http://localhost:8080
```

Use the following bootstrap server when creating a cluster:

```text
kafka1:9092
```

---

# Cluster Architecture

```text
                    Producer
                        |
                        |
       ---------------------------------
       |               |               |
       V               V               V
 localhost:9092 localhost:9093 localhost:9094
       |               |               |
       V               V               V
 +---------+     +---------+     +---------+
 | kafka1  |     | kafka2  |     | kafka3  |
 |         |     |         |     |         |
 | Broker  |     | Broker  |     | Broker  |
 | Ctrl    |     | Ctrl    |     | Ctrl    |
 +---------+     +---------+     +---------+
       \              |              /
        \             |             /
         \            |            /
          ---- Raft Controller ----
                Port 9093

 Broker Replication:
 kafka1:9092 <-> kafka2:9092 <-> kafka3:9092
```

---

# Cluster Details

| Component          | Value        |
| ------------------ | ------------ |
| Kafka Version      | 4.0.0        |
| Brokers            | 3            |
| Controllers        | 3            |
| Replication Factor | 3            |
| KRaft Mode         | Enabled      |
| ZooKeeper          | Not Required |

---

# Ports

| Broker | Internal Port | External Port |
| ------ | ------------- | ------------- |
| kafka1 | 19092         | 9092          |
| kafka2 | 19092         | 9093          |
| kafka3 | 19092         | 9094          |

---

# Useful Commands

### List Topics

```bash
/opt/kafka/bin/kafka-topics.sh \
  --list \
  --bootstrap-server localhost:9092
```

### Describe a Topic

```bash
/opt/kafka/bin/kafka-topics.sh \
  --describe \
  --bootstrap-server localhost:9092
```

### Delete a Topic

```bash
/opt/kafka/bin/kafka-topics.sh \
  --delete \
  --topic orders \
  --bootstrap-server localhost:9092
```

### View Cluster Metadata

```bash
/opt/kafka/bin/kafka-metadata-quorum.sh \
  --bootstrap-server localhost:9092 \
  describe --status
```
