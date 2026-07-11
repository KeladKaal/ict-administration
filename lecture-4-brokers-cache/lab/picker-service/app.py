import os
import json
import time
import threading

from flask import Flask, render_template_string
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("TOPIC", "orders")
GROUP = os.getenv("GROUP", "pickers")
NAME = os.getenv("NAME", "picker-1")

app = Flask(__name__)
feed = []          # лента обработки (для показа на странице)


def consume():
    """Читаем топик в фоне. Подключаемся с повторами, пока Kafka не поднимется."""
    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=BOOTSTRAP,
                group_id=GROUP,
                auto_offset_reset="earliest",
                value_deserializer=lambda v: json.loads(v.decode()),
            )
        except NoBrokersAvailable:
            time.sleep(2)

    for msg in consumer:
        o = msg.value
        feed.insert(0, f"← заказ #{o['order_id']} {o['items']}  (партиция {msg.partition}, offset {msg.offset}) — собираю…")
        time.sleep(2)  # имитация сборки заказа
        feed.insert(0, f"✓ заказ #{o['order_id']} собран  [{NAME}]")


PAGE = """<!doctype html>
<meta charset="utf-8"><meta http-equiv="refresh" content="2">
<title>Сервис сборщика</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:720px;margin:40px auto}
 li{margin:6px 0;font-family:monospace}
</style>
<h1>📦 Сервис сборщика [{{name}}]</h1>
<p>Читает топик <b>{{topic}}</b>, группа потребителей <b>{{group}}</b>.</p>
<h3>Обработка заказов:</h3>
<ul>{% for line in feed %}<li>{{line}}</li>{% endfor %}</ul>
"""


@app.get("/")
def index():
    return render_template_string(PAGE, feed=feed, topic=TOPIC, group=GROUP, name=NAME)


if __name__ == "__main__":
    threading.Thread(target=consume, daemon=True).start()
    app.run(host="0.0.0.0", port=8002)
