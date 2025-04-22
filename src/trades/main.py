# Create an Application instance with Kafka configs


from kraken_api import Trade, krakenAPI
from loguru import logger
from quixstreams import Application


def run(kafka_broker_address: str, kafka_topic_name: str, kraken_api: krakenAPI):
    app = Application(
        broker_address=kafka_broker_address,
    )

    # Define a topic "my_topic" with JSON serialization
    topic = app.topic(name=kafka_topic_name, value_serializer='json')

    # Create a Producer instance
    with app.get_producer() as producer:
        while True:
            events: list[Trade] = kraken_api.get_trades()

            # 1. fetch the event from external API
            # event = {"id": "1", "text": "Lorem ipsum dolor sit amet"}
            for event in events:
                # 2. Serialize an event using the defined Topic
                message = topic.serialize(
                    # key=event["id"],
                    value=event.to_dict()
                )

                # 3. Produce a message into the Kafka topic
                producer.produce(
                    topic=topic.name,
                    value=message.value,
                    # key=message.key
                )

                logger.info(f'Produced message to topic {kafka_topic_name}: {message.value}')


if __name__ == '__main__':
    from trades.config import config

    # create object that can talk to kraken API and get trade data in real time
    api = krakenAPI(product_ids=config.product_ids)

    run(
        # from local system to kafka running in kubernetes cluster
        # kafka_broker_address='localhost:31234',
        # from kubernetes cluster to kafka running in kubernetes cluster
        kafka_broker_address=config.kafka_broker_address,
        kafka_topic_name=config.kafka_topic_name,
        kraken_api=api,
    )
