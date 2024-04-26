from datetime import datetime, timedelta, timezone
from typing import Any

import boto3
from mypy_boto3_ec2.client import EC2Client
from mypy_boto3_ec2.service_resource import Instance as AWSInstance

# Current as of 2024-02-27


class Instance:
    def __init__(self, response: dict[str, Any], client: EC2Client = None):
        self.Tags: dict[str, Any] = {_["Key"]: _["Value"] for _ in response["Tags"]}
        self.Name: str = self.Tags["Name"]
        self._InstanceId: str = response["InstanceId"]
        self._State: str = response["State"]["Name"]
        self._ParentReservation: EC2Client = client
        self._response_dict: dict[str, Any] = response
        self._launch_time: datetime = response["LaunchTime"]
        self._AWSInstance: AWSInstance = boto3.resource("ec2").Instance(self._InstanceId)
        self._UpTime: timedelta | None = datetime.now(tz=timezone.utc) - self._AWSInstance.launch_time
        self._MaxHoursUp: int = 24
        self._AutoShutdown: bool = True
        self._TimeLeft: timedelta | None = None
        self._InstanceType: str = response["InstanceType"]

        if self._AutoShutdown and (self._State == "running"):
            self._TimeLeft = timedelta(minutes=self._MaxHoursUp) - self._UpTime
        elif self._State == "stopped":
            self._TimeLeft = timedelta(minutes=0)

    @property
    def InstanceId(self) -> str:
        return self._InstanceId

    @property
    def InstanceType(self) -> str:
        return self._InstanceType

    @property
    def UpTime(self) -> str:
        return self.convert_display_time(self._UpTime)

    @property
    def UpTimeRaw(self) -> datetime:
        return self._UpTime

    def update_time_left(self) -> timedelta:
        if self.AutoShutdown:
            self._TimeLeft = timedelta(minutes=self._MaxHoursUp) - self._UpTime
        else:
            self._TimeLeft = None

    @property
    def TimeLeft(self) -> str:
        self.update_time_left()
        return self.convert_display_time(self._TimeLeft)

    @property
    def TimeLeftRaw(self) -> timedelta:
        self.update_time_left()
        return self._TimeLeft

    def ResetTimeLeft(self) -> None:
        self._TimeLeft = timedelta(minutes=self._MaxHoursUp)

    @property
    def MaxHoursUp(self):
        return self._MaxHoursUp

    @MaxHoursUp.setter
    def MaxHoursUp(self, max_up) -> None:
        self._MaxHoursUp = max_up

    def set_max_hours_up(self, hours) -> None:
        self._MaxHoursUp = hours

    @property
    def State(self) -> str:
        return self._State

    @State.setter
    def State(self, update) -> None:
        self._State = update

    @property
    def AutoShutdown(self) -> bool:
        return self._AutoShutdown

    @AutoShutdown.setter
    def AutoShutdown(self, state) -> None:
        self._AutoShutdown = state

    def update_up_time(self) -> str:
        self.update_status()
        if self.State == "running":
            self._UpTime = datetime.now(tz=timezone.utc) - self._AWSInstance.launch_time
        else:
            self._UpTime = None

        if self._UpTime is None:
            return f"{self.Name} is not running"
        else:
            return self.convert_display_time(self._UpTime)

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

    def convert_display_time(self, timevalue: timedelta | None = None) -> str:
        # if you need more than days here, find Jesus, touch grass, whatever
        # but get away from the GPU
        if timevalue is None:
            return "--:--:--"
        else:
            days = timevalue.total_seconds() // (24 * 60 * 60)
            hours = (timevalue - timedelta(days=days)).total_seconds() // (60 * 60)
            minutes = (timevalue - timedelta(days=days, hours=hours)).total_seconds() // 60
            seconds = (timevalue - timedelta(days=days, hours=hours, minutes=minutes)).total_seconds()
            return f"{str(int(days)).zfill(2)}:{str(int(hours)).zfill(2)}:{str(int(minutes)).zfill(2)}:{str(int(seconds)).zfill(2)}"

    def __repr__(self) -> str:
        return (
            f"Name: {self.Name}, InstanceId: {self.InstanceId}, InstanceType: {self.InstanceType}, State: {self.State}"
        )


class Reservation:
    def __init__(self, client):
        response = client.describe_instances()
        self.Instances = [Instance(_["Instances"][0], client) for _ in response["Reservations"]]
        self.InstanceDict: dict[str, Instance] = {_.Name: _ for _ in self.Instances}

    def __getitem__(self, name) -> Instance:
        return self.InstanceDict[name]

    def __repr__(self) -> str:
        instance_names = "\n".join(
            f"Name: {_.Name}: InstanceId: {_.InstanceId}, State: {_.State}, InstanceType: {_.InstanceType}"
            for _ in self.Instances
        )
        return instance_names
