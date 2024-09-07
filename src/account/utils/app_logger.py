import logging


class AppLogger:
    def __init__(self, log_name):
        self.logger = logging.getLogger(log_name)
        logging.basicConfig(
            level=logging.INFO,
            format="[%(name)s] [%(levelname)s] %(message)s",
            handlers=[logging.StreamHandler()],
        )

    def info(self, msg):
        self.logger.info(msg)
