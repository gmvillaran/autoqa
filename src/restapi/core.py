import logging
import os

from elasticapm.contrib.starlette import make_apm_client
from pydantic import BaseSettings
from pytz import timezone

from utils.aws_connection_helper import EC2Instance
from utils.influxdb_helper import setup_influxdb
from utils.logger_helper import ElasticAPMLogHandler, Logger, SlackLogHandler

ec2_obj = EC2Instance()


class Settings(BaseSettings):
    API_STR: str = "/api"
    APM_SERVICE_NAME: str
    APM_SERVER_URL: str
    PROJECT_NAME: str = "AutoQA"
    TIMEZONE = timezone("US/EASTERN")
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_DATEFMT: str
    LOG_FILE: str
    INFLUXDB_HOST: str
    INFLUXDB_DB_NAME: str
    SLACK_WEBHOOK_URL: str
    SLACK_LOG_ENABLED: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Config:
        case_sensitive = True
        env_file = os.path.realpath("..") + "/config.ini"


def setup_logger(settings: Settings) -> Logger:
    logger_obj = Logger(
        logger_name=__name__,
        log_format=settings.LOG_FORMAT,
        datefmt=settings.LOG_DATEFMT,
        filename=settings.LOG_FILE,
    )

    if settings.SLACK_LOG_ENABLED or ec2_obj.env in ["production", "prod"]:
        slack_log_handler = SlackLogHandler(
            url=settings.SLACK_WEBHOOK_URL,
            title=settings.PROJECT_NAME,
            level=logging.CRITICAL,
        )
        logger_obj.add_handler(slack_log_handler)

    if apm_client:
        apm_log_handler = ElasticAPMLogHandler(apm_client)
        logger_obj.add_handler(apm_log_handler)

    logger = logger_obj.logger
    return logger


def setup_apm(settings: Settings) -> make_apm_client:
    if not ec2_obj.is_ec2_instance:
        return None

    apm_config = {
        "SERVICE_NAME": settings.APM_SERVICE_NAME,
        "SERVER_URL": settings.APM_SERVER_URL,
        "ENVIRONMENT": ec2_obj.env,
    }
    apm_client = make_apm_client(apm_config)
    return apm_client


settings = Settings()
apm_client = setup_apm(settings)
logger = setup_logger(settings)
monitor_db = setup_influxdb(
    ec2=ec2_obj,
    influxdb_host=settings.INFLUXDB_HOST,
    influxdb_db_name=settings.INFLUXDB_DB_NAME,
    logger=logger,
)
