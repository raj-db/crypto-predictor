from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kafka_broker_address: str
    kafka_input_topic: str
    kafka_output_topic: str
    candle_seconds: int
    emit_intermediate_candles: bool

    model_config = SettingsConfigDict(env_file='services/candles/settings.env')


config = Settings()

print(config.model_dump())
