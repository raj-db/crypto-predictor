from loguru import logger
from quixstreams import Application


def init_candle(trade: dict) -> dict:
    # initialize a candle with the first trade
    # returns the initial state for the candle
    return {
        'product_id': trade['product_id'],
        #'timestamp': trade['timestamp'],
        'open': trade['price'],
        'high': trade['price'],
        'low': trade['price'],
        'close': trade['price'],
        'volume': trade['quantity'],
    }


def update_candle(candle: dict, trade: dict) -> dict:
    # update the candle with the new trade
    # returns the updated state for the candle
    # open price doesn't change so no need to update it
    candle['high'] = max(candle['high'], trade['price'])
    candle['low'] = min(candle['low'], trade['price'])
    candle['close'] = trade['price']
    candle['volume'] += trade['quantity']
    return candle


def run(
    # kafka parameters
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_consumer_group: str,
    # Candle parameters
    candle_seconds: int,
    emit_intermediate_candles: bool,
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
        consumer_group=kafka_consumer_group,
    )

    # Define the Kafka topics
    trades_topic = app.topic(kafka_input_topic, value_deserializer='json')
    candles_topic = app.topic(kafka_output_topic, value_serializer='json')

    # Create a Streaming DataFrame connected to the input Kafka topic
    sdf = app.dataframe(topic=trades_topic)

    # aggregate trades into candles using tumbling window

    from datetime import timedelta

    sdf = (
        # define a tumbling window of 10 mins
        sdf.tumbling_window(timedelta(seconds=candle_seconds))
        # create a reduce aggregation with reducer and initializer functions
        .reduce(
            reducer=update_candle,
            initializer=init_candle,
        )
    )

    if emit_intermediate_candles:
        # emit all the intermediate candles to make the system more responsive
        sdf = sdf.current()
    else:
        # emit only the final candle after the window is closed
        sdf = sdf.final()

    # Extract open, high, low, close, volume ,timestamp_ms,pair from the dataframe
    sdf['open'] = sdf['value']['open']
    sdf['high'] = sdf['value']['high']
    sdf['low'] = sdf['value']['low']
    sdf['close'] = sdf['value']['close']
    sdf['volume'] = sdf['value']['volume']
    # sdf['timestamp_ms']=sdf['value']['timestamp_ms']
    sdf['product_id'] = sdf['value']['product_id']

    # Extract the timestamp_ms from the dataframe
    sdf['window_start_ms'] = sdf['start']
    sdf['window_end_ms'] = sdf['end']

    # Keep only the relevant columns , excluding 'timestamp_ms'
    sdf = sdf[
        ['product_id', 'open', 'high', 'low', 'close', 'volume', 'window_start_ms', 'window_end_ms']
    ]

    sdf['candle_seconds'] = candle_seconds

    # Print the input data
    # logging.basicConfig(level=logging.INFO)
    # logger = logging.getLogger(__name__)
    # logging the data to the console
    sdf = sdf.update(lambda value: logger.debug(f'Candle:  {value}'))

    # Produce alerts to the output topic
    sdf = sdf.to_topic(candles_topic)

    # starts the streaming app
    app.run()


if __name__ == '__main__':
    from candles.config import config

    run(
        kafka_broker_address=config.kafka_broker_address,
        kafka_input_topic=config.kafka_input_topic,
        kafka_output_topic=config.kafka_output_topic,
        candle_seconds=config.candle_seconds,
        kafka_consumer_group=config.kafka_consumer_group,
        emit_intermediate_candles=config.emit_intermediate_candles,
    )
