import os
import json
from flask import current_app
from flask import g
from kafka import KafkaConsumer
from kafka import KafkaProducer
from threading import Thread
import logging


from api import metrics
from app import db
from app.logging import threadctx
from app.models import Host, SystemProfileSchema

logger = logging.getLogger(__name__)

TOPIC = os.environ.get("KAFKA_TOPIC", "platform.system-profile")
KAFKA_GROUP = os.environ.get("KAFKA_GROUP", "inventory")
BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
logger.debug(f"BOOTSTRAP_SERVERS: {BOOTSTRAP_SERVERS}")
EVENT_TOPIC = os.environ.get("KAFKA_EVENT_TOPIC", "platform.inventory.events")


class TestProducer:
    def __init__(self, *args, **kwargs):
        self.init_args = args
        self.init_kwargs = kwargs
        self.pending_messages = {}
        self.sent_messages = {}

    def send(self, topic, value=None, key=None, partition=None, timestamp_ms=None):
        if topic not in self.pending_messages:
            self.pending_messages[topic] = []
        self.pending_messages[topic].append({
            "value": value,
            "key": key,
            "partition": partition,
            "timestamp_ms": timestamp_ms
        })

    def flush(self):
        for topic, pending_messages in self.pending_messages.items():
            if topic not in self.sent_messages:
                self.sent_messages[topic] = []
            while True:
                try:
                    message = pending_messages.pop()
                except IndexError:
                    break
                else:
                    self.sent_messages[topic].append(message)


class _EventProducer:
    def __init__(self):
        producer_class = current_app.config["producer_class"] or KafkaProducer
        self.producer = producer_class(bootstrap_servers=BOOTSTRAP_SERVERS)

    def emit_event(self, e):
        self.producer.send(EVENT_TOPIC, value=e.encode("utf-8"))
        self.producer.flush()


@metrics.system_profile_commit_processing_time.time()
def msg_handler(parsed):
    id_ = parsed["id"]
    threadctx.request_id = parsed["request_id"]
    if not id_:
        logger.error("ID is null, something went wrong.")
        return
    host = Host.query.get(id_)
    if host is None:
        logger.error("Host with id [%s] not found!", id_)
        return
    logger.info("Processing message id=%s request_id=%s", parsed["id"], parsed["request_id"])
    profile = SystemProfileSchema(strict=True).load(parsed["system_profile"]).data
    host._update_system_profile(profile)
    db.session.commit()


def get_producer():
    if "producer" not in g:
        g.producer = _EventProducer()
    return g.producer


def start_consumer(flask_app, handler=msg_handler, consumer=None):

    logger.info("Starting system profile queue consumer.")

    if consumer is None:
        consumer = KafkaConsumer(
            TOPIC,
            group_id=KAFKA_GROUP,
            bootstrap_servers=BOOTSTRAP_SERVERS)

    def _f():
        with flask_app.app_context():
            while True:
                for msg in consumer:
                    try:
                        with metrics.system_profile_deserialization_time.time():
                            data = json.loads(msg.value)
                        handler(data)
                        metrics.system_profile_commit_count.inc()
                    except Exception:
                        logger.exception("uncaught exception in handler, moving on.")
                        metrics.system_profile_failure_count.inc()

    t = Thread(
        target=_f,
        daemon=True)
    t.start()
