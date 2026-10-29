import boto3
from mypy_boto3_ec2.client import EC2Client
from mypy_boto3_ec2.service_resource import Instance as AWSInstance
from datetime import datetime, timezone
from typing import Any


class Instance:
    def __init__(self, response: dict[str, Any], client: EC2Client = None):
        self.Tags: dict[str, Any] = {_["Key"]: _["Value"] for _ in response["Tags"]}
        self.Name: str = self.Tags["Name"]
        self._InstanceId: str = response["InstanceId"]
        self._State: str = response["State"]["Name"]
        self._ParentReservation: EC2Client = client
        self._response_dict: dict[str, Any] = response
        self._launch_time: datetime.datetime = response["LaunchTime"]
        self._AWSInstance: AWSInstance = boto3.resource("ec2").Instance(self._InstanceId)
        self._UpTime: datetime.timedelta | None = datetime.now(tz=timezone.utc) - self._AWSInstance.launch_time

    @property
    def InstanceId(self) -> str:
        return self._InstanceId

    @property
    def UpTime(self) -> str:
        return str(self._UpTime).split(".")[0]

    @property
    def UpTimeRaw(self) -> datetime:
        return self._UpTime

    def UpdateUpTime(self) -> str:
        self.update_status()
        if self.State == "running":
            self._UpTime = datetime.now(tz=timezone.utc) - self._AWSInstance.launch_time
        else:
            self._UpTime = None

        if self._UpTime is None:
            return f"{self.Name} is not running"
        else:
            return str(self._UpTime).split(".")[0]

    @property
    def State(self) -> str:
        return self._State

    @State.setter
    def State(self, update) -> None:
        self._State = update

    def update_status(self) -> str:
        self._AWSInstance.load()
        self.State = self._AWSInstance.state["Name"]
        return self.State

    # async def start_instance(self) -> str:
    def start_instance(self) -> str:
        self._AWSInstance.start()
        self.State = "starting up"
        # self._AWSInstance.wait_until_running()
        # self.update_status()
        return self.State

    # async def stop_instance(self) -> str:
    def stop_instance(self) -> str:
        self._AWSInstance.stop()
        self.State = "shutting down"
        # self._AWSInstance.wait_until_stopped()
        # self.update_status()
        return self.State

    def __repr__(self) -> str:
        return f"Name: {self.Name}, InstanceId: {self.InstanceId}, State: {self.State}"


class Reservation:
    def __init__(self, client):
        response = client.describe_instances()
        self.Instances = [Instance(_["Instances"][0], client) for _ in response["Reservations"]]
        self.InstanceDict: dict[str, Instance] = {_.Name: _ for _ in self.Instances}

    def __getitem__(self, name) -> Instance:
        return self.InstanceDict[name]

    def __repr__(self) -> str:
        instance_names = "\n".join(
            f"Name: {_.Name}: InstanceId: {_.InstanceId}, State: {_.State}" for _ in self.Instances
        )
        return instance_names
