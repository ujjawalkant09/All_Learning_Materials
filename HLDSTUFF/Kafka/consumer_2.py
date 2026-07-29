import json

from confluent_kafka import Consumer


consumer = Consumer(
    {
        "bootstrap.servers": "localhost:9092,localhost:9093,localhost:9094",
        "group.id": "orders-group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit":False,
    }
)

consumer.subscribe(["orders_v2"])

print("Consumer started...2*******")


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
            f"Partition2*******={msg.partition()} "
            f"Offset2*******={msg.offset()} "
            f"Data2*******={data}"
        )
        consumer.commit(message=msg)

finally:
    consumer.close()