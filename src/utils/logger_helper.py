import logging

import psutil
import slack_sdk


class ElasticAPMLogHandler(logging.Handler):
    def __init__(self, apm_client):
        super().__init__(logging.ERROR)
        self.apm_client = apm_client

    def emit(self, record):
        try:
            message = self.format(record)
            self.apm_client.capture_message(f"{record.levelname} {message}")

        except Exception:
            self.handleError(record)


class SlackLogHandler(logging.Handler):
    def __init__(
        self,
        color: str = None,
        env: str = "local",
        level=logging.ERROR,
        token: str = None,
        title: str = None,
        url: str = None,
        channel: str = None,
    ) -> None:
        if all([token, url]) is None:
            raise ValueError("Slack token/url is required")
        self.token = token
        self.url = url
        self.channel = channel
        self.env = env.capitalize()

        color_env_map = dict(
            dev="#9FF348",
            qa="#F3F248",
            staging="#F39C48",
            stg="#F39C48",
            prod="#F34849",
            production="#F34849",
        )
        if color:
            self.color = color
        else:
            self.color = color_env_map.get(self.env, "#FFFFFF")

        self.title = title
        super().__init__(level)

    def emit(self, record):
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent
        ram_usage = psutil.virtual_memory().used / (1024**3)  # in GB
        message = {
            "text": f"*{self.env} Alert*",
            "attachments": [
                {
                    "color": self.color,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": ":rotating_light: Error Alert!",
                            },
                        },
                        {"type": "divider"},
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*{self.title}*\nError message:\n"
                                    f"```{record}```"
                                ),
                            },
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "plain_text",
                                    "emoji": True,
                                    "text": ":warning:",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": (
                                        "*Kindly acknowledge this alert"
                                        " by replying to this thread*"
                                    ),
                                },
                            ],
                        },
                        {"type": "divider"},
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Current Server Status:*\n",
                            },
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*CPU Usage:* {cpu_usage} %",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Memory Usage:* {mem_usage} %",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*RAM Usage:* {ram_usage:.2f} GB",
                                },
                            ],
                        },
                    ],
                }
            ],
        }
        try:
            client = slack_sdk.WebhookClient(url=self.url)
            client.send_dict(message)
        except Exception:
            pass


class Logger:
    def __init__(
        self,
        logger_name: str = None,
        log_format: str = None,
        datefmt: str = None,
        level: logging = logging.INFO,
        filename: str = None,
    ):
        if filename is None:
            raise ValueError("Filename must be specified")

        self.log_format = log_format
        self.datefmt = datefmt
        self.level = level
        self.filename = filename
        self.name = logger_name
        self._logger = self._setup_logger()

    def _setup_logger(self):
        logging.basicConfig(
            format=self.log_format,
            datefmt=self.datefmt,
            level=self.level,
            filename=self.filename,
        )

        return logging.getLogger(self.name)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger

    def add_handler(self, handler):
        self.logger.addHandler(handler)

    def add_filter(self, filter):
        self.logger.addFilter(filter)
