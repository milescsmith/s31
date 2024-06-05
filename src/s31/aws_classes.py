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
        self._instance_id: str = response["InstanceId"]
        self._state: str = response["State"]["Name"]
        self._parent_reservation: EC2Client = client
        self._response_dict: dict[str, Any] = response
        self._launch_time: datetime = response["LaunchTime"]
        self._aws_instance: AWSInstance = boto3.resource("ec2").Instance(self._instance_id)
        self._uptime: timedelta | None = datetime.now(tz=timezone.utc) - self._aws_instance.launch_time
        self._max_hours_up: int = 24
        self._auto_shutdown: bool = True
        self._time_left: timedelta | None = None
        self._instance_type: str = response["InstanceType"]
        self._shutdown_time: datetime | None = None

        if self._auto_shutdown and (self._state == "running"):
            self._time_left = timedelta(minutes=self._max_hours_up) - self._uptime
        elif self._state == "stopped":
            self._time_left = timedelta(minutes=0)

    # object property getters and setters
    @property
    def auto_shutdown(self) -> bool:
        return self._auto_shutdown

    @auto_shutdown.setter
    def auto_shutdown(self, state: bool = True) -> None:
        self._auto_shutdown = state

    @property
    def instance_id(self) -> str:
        return self._instance_id

    @property
    def instance_type(self) -> str:
        return self._instance_type

    @property
    def max_hours_up(self):
        return self._max_hours_up

    @max_hours_up.setter
    def max_hours_up(self, max_up) -> None:
        self._max_hours_up = max_up

    @max_hours_up.deleter
    def max_hours_up(self) -> None:
        del self._max_hours_up

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, update) -> None:
        self._state = update
    
    @property
    def time_left(self) -> str:
        self._update_time_left()
        return self.convert_display_time(self._time_left)

    @property
    def time_left_raw(self) -> timedelta:
        self._update_time_left()
        return self._time_left

    @property
    def uptime(self) -> str:
        return self.convert_display_time(self._uptime)

    @property
    def uptime_raw(self) -> datetime:
        return self._uptime

    # object methods
    def set_tag(self, key, value):
        pass
    
    def reset_time_left(self) -> None:
        self._time_left = timedelta(minutes=self._max_hours_up)
    
    def update_status(self) -> str:
        self._aws_instance.load()
        self.state = self._aws_instance.state["Name"]
        return self.state
    
    def _update_time_left(self) -> timedelta:
        if self.auto_shutdown:
            self._time_left = timedelta(minutes=self._max_hours_up) - self._uptime
        else:
            self._time_left = None
    
    def _update_uptime(self) -> str:
        self.update_status()
        if self.state == "running":
            self._uptime = datetime.now(tz=timezone.utc) - self._aws_instance.launch_time
        else:
            self._uptime = None

        if self._uptime is None:
            return f"{self.Name} is not running"
        else:
            return self.convert_display_time(self._uptime)

    # async def start_instance(self) -> str:
    def start_instance(self) -> str:
        self._aws_instance.start()
        self.state = "starting up"
        # self._AWSInstance.wait_until_running()
        # self.update_status()
        if self.max_uptime:
            self._shutdown_time = datetime.now() + timedelta(hours=self.max_uptime)
        else:
            self.auto_shutdown = False
            self._shutdown_time = datetime.now() + timedelta(days=365)
        return self.state

    # async def stop_instance(self) -> str:
    def stop_instance(self) -> str:
        self._aws_instance.stop()
        self.state = "shutting down"
        # self._AWSInstance.wait_until_stopped()
        # self.update_status()
        return self.state

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
            f"Name: {self.Name}, InstanceId: {self.instance_id}, InstanceType: {self.instance_type}, State: {self.state}"
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
            f"Name: {_.Name}: InstanceId: {_.instance_id}, State: {_.state}, InstanceType: {_.instance_type}"
            for _ in self.Instances
        )
        return instance_names
