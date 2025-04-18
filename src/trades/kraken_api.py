from pydantic import BaseModel
import json
from websocket import create_connection
from loguru import logger

class Trade(BaseModel):
    product_id: str
    price: float
    quantity: float
    timestamp: str  

    #convert the Trade object to a dictionary
    def to_dict(self) -> dict:
        return self.model_dump()

class krakenAPI:
    url= 'wss://ws.kraken.com/v2'
    def __init__(
        self,
        product_ids: list[str]
    ):

        
        self.product_ids=product_ids

        #create a websocket client
        self._ws_client= create_connection(self.url)

        

        #send initial subscription message  
        self._subscribe(product_ids)
        

    def get_trades(self) -> list[Trade]:
        data = self._ws_client.recv()

        
        # if heartbeat is received, return an empty list
        if 'heartbeat' in data:
            logger.info('heartbeat received')
            return []
        

        # Transform raw string into JSON object
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f'Error decoding JSON: {e}')
            return []
        
        # Extract trade data from the JSON object
        try:
            trades_data = data['data']
        except KeyError as e:
            logger.error(f'No data field with trades in the message {e}')
            return []
        

        # append data from trades_data to the trades list
        trades = []
        # for trade in trades_data:
        #     trades.append(Trade(
        #         product_id=trade['symbol'],
        #         price=trade['price'],
        #         quantity=trade['qty'],
        #         timestamp=trade['timestamp']
        #     ))
        # breakpoint()

        #list comprehension
        trades = [Trade(
            product_id=trade['symbol'],
            price=trade['price'],
            quantity=trade['qty'],
            timestamp=trade['timestamp']
        ) for trade in trades_data]
        return trades
       
    
    def _subscribe(self, product_ids: list[str]):

        #subscribe to the websocket for a given product ids and wait for the initial snapshot
        self._ws_client.send(
            json.dumps(
                {
                    "method": "subscribe",
                    "params": {
                            "channel": "trade",
                            "symbol": product_ids,
                            "snapshot": False
                            }
                }
            )
        )
       
        # discard the first 2 messages for each product id as they contain no trade data
        for _ in self.product_ids:
            _ =self._ws_client.recv()
            _ =self._ws_client.recv()
    

        #print("Sending subscribe message:", subscribe_message)
        #self._ws_client.send(json.dumps(subscribe_message))
        #breakpoint()


