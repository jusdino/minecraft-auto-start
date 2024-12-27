from server import Server
from config import Config, logger
from schema import InvokeEventSchema


config = Config()
schema = InvokeEventSchema()


def main(event: dict, context) -> None:
    """
    Entrypoint for lambda
    """
    event = schema.load(event)
    server_name = event['server_name']
    logger.info('Processing event for %s', server_name)
    instance_config = event['instance_configuration']

    server = Server(
        config=config,
        logger=logger,
        server_name=server_name
    )
    server.launch(
        **instance_config
    )
