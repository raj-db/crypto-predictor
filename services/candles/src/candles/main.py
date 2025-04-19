from loguru import logger
from quixstreams import Application


def run(
    # kafka parameters
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_output_topic: str,
    # Candle parameters
    candle_sec: int,
):
    """
    transform a stream of input trades into a stream of output candles

    in 3 steps:
    - ingest trade from the kafka_input_topic
    - aggregate trades into candles
    - write candles to the kafka_output_topic

    Args:
        kafka_broker_address:str
        kafka_input_topic:str
        kafka_output_topic:str
        candle_sec:int

    Returns:
        None
    """
    # create an application
    app = Application(
        broker_address=kafka_broker_address,
    )

    # Define the Kafka topics
    trades_topic = app.topic(kafka_input_topic, value_deserializer='json')
    candles_topic = app.topic(kafka_output_topic, value_serializer='json')

    # Create a Streaming DataFrame connected to the input Kafka topic
    sdf = app.dataframe(topic=trades_topic)

    # Print the input data
    # logging.basicConfig(level=logging.INFO)
    # logger = logging.getLogger(__name__)
    sdf = sdf.update(lambda message: logger.info(f'Input:  {message}'))

    # Produce alerts to the output topic
    sdf = sdf.to_topic(candles_topic)

    # starts the streaming app
    app.run()


if __name__ == '__main__':
    run(
        kafka_broker_address='localhost:31234',
        kafka_input_topic='trades',
        kafka_output_topic='candles',
        candle_sec=60,
    )
