import socket
import urllib.request

import boto3


class EC2Instance:
    def __init__(self) -> None:
        self._metadata_url = "http://169.254.169.254/latest/meta-data/"
        self.timeout = 5
        try:
            self.local_ipv4 = self.get_metatadata("local-ipv4")
            self.instance_id = self.get_metatadata("instance-id")
            self.availability_zone = self.get_metatadata(
                "placement/availability-zone"
            )
            self.region_name = self.get_metatadata("placement/region")
            self.tags = self.get_tags() or dict()
            self.env = self.tags.get("Environment")
        except (urllib.error.URLError, socket.timeout):
            self.is_ec2_instance = False
            # Replace env to dev when running scripts locally.
            # Using "local" here is for safety reasons only.
            self.env = "local"
            self.region_name = None
        else:
            self.is_ec2_instance = True

    def get_metatadata(self, field) -> str:
        value = (
            urllib.request.urlopen(
                f"{self._metadata_url}{field}", timeout=self.timeout
            )
            .read()
            .decode("utf-8")
        )
        return value

    def get_tags(self) -> dict:
        ec2 = boto3.resource("ec2", region_name=self.region_name)
        running_instances = ec2.instances.filter(
            Filters=[{"Name": "tag:App", "Values": ["AutoQA"]}]
        )

        current_instance = None
        for instance in running_instances:
            if instance.private_ip_address == self.local_ipv4:
                current_instance = instance
                break

        tags = {tag["Key"]: tag["Value"] for tag in current_instance.tags}
        return tags

    def get_from_paramstore(self, key):
        ssm = boto3.client("ssm", region_name=self.region_name)
        param = ssm.get_parameter(Name=key)["Parameter"]
        if param.get("Type") == "SecureString":
            return ssm.get_parameter(Name=key, WithDecryption=True)[
                "Parameter"
            ]["Value"]
        else:
            return param.get("Value")

    def start_instance(self, instance_id):
        ec2 = boto3.client("ec2", region_name=self.region_name)
        ec2.start_instances(InstanceIds=[instance_id])

    def stop_instance(self, instance_id):
        ec2 = boto3.client("ec2", region_name=self.region_name)
        ec2.stop_instances(InstanceIds=[instance_id])

    def check_instance_status(self, instance_ids):
        client = boto3.client("ec2")
        try:
            response = client.describe_instance_status(
                InstanceIds=instance_ids,
            ).get("InstanceStatuses")
        except Exception:
            return "ERROR"
        if isinstance(response, list) and len(response) > 0:
            instance_state = response[0].get("InstanceState", {}).get("Name")
            return instance_state

        else:
            return "OFFLINE"
