import time

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError

from utils.aws_connection_helper import EC2Instance


def setup_influxdb(
    ec2: EC2Instance,
    influxdb_host,
    influxdb_db_name,
    logger=None,
    pool_size: int = 200,
) -> InfluxDBClient:
    if not ec2.is_ec2_instance:
        return None
    try:
        client = InfluxDBClient(
            host=influxdb_host,
            database=influxdb_db_name,
            pool_size=pool_size,
        )
    except (InfluxDBClientError, InfluxDBServerError) as error:
        if logger:
            logger.warning("InfluxDBClient error: %s", str(error))
    return client


def influx_writer(
    client: InfluxDBClient = None,
    ec2: EC2Instance = None,
    field_map: dict = None,
    logger=None,
    measurement: str = "ai-ute-whisper",
) -> None:
    if client is None or ec2 is None or field_map is None:
        return

    try:
        current_time = int(round(time.time() / 60) * 60)
        data = [
            {
                "measurement": measurement,
                "tags": {
                    "host": ec2.tags.get("Name"),
                    "site": ec2.availability_zone,
                    "host_ip": ec2.local_ipv4,
                },
                "fields": field_map,
                "time": current_time,
            }
        ]
        client.write_points(data, time_precision="s")
    except Exception as error:
        if logger:
            logger.error("Failed writing to influx db %s", error)
