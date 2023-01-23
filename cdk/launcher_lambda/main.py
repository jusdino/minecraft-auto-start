from server import Server
from config import Config, logger


config = Config()


def main(event: dict, context) -> None:
    """
    Entrypoint for lambda
    """
    server_name = event['server_name']
    logger.info('Processing event for %s', server_name)
    instance_type = event['instance_type']
    volume_size = event['volume_size']
    memory_size = event['memory_size']

    server = Server(
        config=config,
        logger=logger,
        server_name=server_name
    )
    server.launch(
        instance_type=instance_type,
        volume_size=volume_size,
        memory_size=memory_size
    )
