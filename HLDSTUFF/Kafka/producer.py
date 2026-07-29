import json
import random
import time

from confluent_kafka import Producer


producer = Producer(
    {
        "bootstrap.servers": "localhost:9092,localhost:9093,localhost:9094"
    }
)


def delivery_report(err, msg):
    if err:
        print(f"Failed: {err}")
    else:
        print(
            f"Topic={msg.topic()} "
            f"Partition={msg.partition()} "
            f"Offset={msg.offset()}"
        )


while True:

    order_id = random.randint(1000, 9999)

    payload = {
        "order_id": order_id,
        "amount": random.randint(100, 5000),
        "Test_Value":f"New Value {order_id}"
    }

    producer.produce(
        topic="orders_v2",
        value=json.dumps(payload),
        callback=delivery_report
    )


    producer.poll(0)

    time.sleep(1)