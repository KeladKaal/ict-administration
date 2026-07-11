import os
import json
import random
import time

from flask import Flask, render_template_string, redirect
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("TOPIC", "orders")
ITEMS = ["молоко", "хлеб", "яйца", "бананы", "кофе", "сыр", "вода", "яблоки", "чай", "макароны"]

app = Flask(__name__)
sent = []          # что уже отправили (для показа на странице)
next_id = 1
_producer = None


def producer():
    """Подключаемся к Kafka с повторами — брокер может подниматься дольше сервиса."""
    global _producer
    while _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP,
                key_serializer=lambda k: str(k).encode(),
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode(),
            )
        except NoBrokersAvailable:
            time.sleep(2)
    return _producer


PAGE = """<!doctype html>
<meta charset="utf-8"><meta http-equiv="refresh" content="3">
<title>Сервис пользователя</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:720px;margin:40px auto}
 button{font-size:18px;padding:10px 22px;cursor:pointer}
 li{margin:6px 0;font-family:monospace}
</style>
<h1>🧑 Сервис пользователя (заказы)</h1>
<form method="post" action="/order"><button>➕ Создать заказ</button></form>
<p>Кладёт событие «заказ создан» в топик <b>{{topic}}</b> (ключ = order_id).</p>
<h3>Отправленные заказы:</h3>
<ul>{% for line in sent %}<li>{{line}}</li>{% endfor %}</ul>
"""


@app.post("/order")
def order():
    global next_id
    oid = next_id
    next_id += 1
    items = random.sample(ITEMS, k=random.randint(1, 3))
    event = {"order_id": oid, "items": items, "status": "создан"}
    meta = producer().send(TOPIC, key=oid, value=event).get(timeout=10)
    sent.insert(0, f"→ заказ #{oid} {items}  →  партиция {meta.partition}, offset {meta.offset}")
    return redirect("/")


@app.get("/")
def index():
    return render_template_string(PAGE, sent=sent, topic=TOPIC)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
