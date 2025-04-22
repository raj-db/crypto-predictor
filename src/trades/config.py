from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kafka_broker_address: str
    product_ids: list[str] = ['BTC/EUR']
    kafka_topic_name: str

    model_config = SettingsConfigDict(env_file='services/trades/settings.env')


config = Settings()

print(config.model_dump())
