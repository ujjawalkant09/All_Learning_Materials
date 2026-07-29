import json

from confluent_kafka import Consumer


consumer = Consumer(
    {
        "bootstrap.servers": "localhost:9092,localhost:9093,localhost:9094",
        "group.id": "billing-service",
        "auto.offset.reset": "earliest",
        "enable.auto.commit":False,
    }
)

consumer.subscribe(["orders_v2"])

print("Consumer started...")


try:

    while True:

        msg = consumer.poll(1)

        if msg is None:
            continue

        if msg.error():
            print(msg.error())
            continue

        data = json.loads(
            msg.value().decode()
        )

        print(
            f"Partition={msg.partition()} "
            f"Offset={msg.offset()} "
            f"Data={data}"
        )
        consumer.commit(message=msg)

finally:
    consumer.close()