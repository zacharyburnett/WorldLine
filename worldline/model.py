from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union

from matplotlib import pyplot
from matplotlib.axis import Axis
from matplotlib.collections import LineCollection
import numpy
from pandas import DataFrame
import typepigeon as typepigeon

from worldline.utilities import fill_3D_vector


class SpaceTimeLocation:
    def __init__(
        self,
        location: Tuple[float, Optional[float], Optional[float]],
        velocity: Tuple[float, Optional[float], Optional[float]] = None,
        time: datetime = None,
    ):
        if velocity is None:
            velocity = 0

        if time is None:
            time = timedelta(0)
        else:
            try:
                time = typepigeon.convert_value(time, timedelta)
            except TypeError:
                time = typepigeon.convert_value(time, datetime)

        self.__location = numpy.array(fill_3D_vector(location))
        self.__velocity = numpy.array(fill_3D_vector(velocity))
        self.__time = time

    @property
    def location(self) -> numpy.ndarray:
        return self.__location

    @property
    def velocity(self) -> numpy.ndarray:
        return self.__velocity

    @property
    def time(self) -> Union[timedelta, datetime]:
        return self.__time

    def distance(self, other: "SpaceTimeLocation") -> float:
        return

    def __sub__(self, other: "SpaceTimeLocation") -> "SpaceTimeLocation":
        return SpaceTimeLocation(
            location=self.location - other.location,
            velocity=self.velocity - other.velocity,
            time=self.time - other.time,
        )


class SpatioTemporal:
    def __init__(
        self,
        starting_location: Tuple[float, Optional[float], Optional[float]],
        starting_velocity: Tuple[float, Optional[float], Optional[float]] = None,
        starting_time: datetime = None,
        name: str = None,
    ):
        self.start = SpaceTimeLocation(
            location=starting_location, velocity=starting_velocity, time=starting_time
        )

        self.__velocities = DataFrame(
            {
                "time": [self.start.time],
                "x": [self.start.velocity[0]],
                "y": [self.start.velocity[1]],
                "z": [self.start.velocity[2]],
            }
        ).set_index("time")

        self.__events = DataFrame(
            columns=["time", "name", "propagation_speed"]
        ).set_index("time")
        self.name = name

    @property
    def velocities(self) -> DataFrame:
        return self.__velocities

    @property
    def events(self) -> DataFrame:
        return self.__events

    @property
    def locations(self) -> DataFrame:
        velocities = self.__velocities

        locations = DataFrame.from_records(
            [self.location_at_time(time) for time in velocities.index],
            columns=["x", "y", "z"],
            index=velocities.index,
        )

        return locations

    @property
    def times(self) -> List[datetime]:
        times = self.locations.index.values
        if times.dtype.type != numpy.timedelta64:
            times -= self.start.time
        times = times / numpy.array(1, "<m8[s]")
        return times

    def add_velocity_change(
        self,
        time: Union[datetime, timedelta],
        velocity: Tuple[float, Optional[float], Optional[float]],
    ):
        try:
            time = typepigeon.convert_value(time, timedelta)
        except TypeError:
            time = typepigeon.convert_value(time, datetime) - self.start.time
        velocity = fill_3D_vector(velocity)
        self.__velocities.loc[time] = (velocity[0], velocity[1], velocity[2])
        self.__velocities.sort_index(inplace=True)

    def add_event(
        self, time: Union[datetime, timedelta], name: str, propagation_speed: float
    ):
        try:
            time = typepigeon.convert_value(time, timedelta)
        except TypeError:
            time = typepigeon.convert_value(time, datetime) - self.start.time
        self.__events.loc[time] = [name, propagation_speed]
        self.__events.sort_index(inplace=True)

    def velocity(self, time: Union[datetime, timedelta]) -> numpy.ndarray:
        try:
            time = typepigeon.convert_value(time, timedelta)
        except TypeError:
            time = typepigeon.convert_value(time, datetime) - self.start.time
        velocities = self.__velocities
        if time in velocities.index:
            velocity = velocities.loc[time]
        else:
            index = velocities.index.searchsorted(time)
            if time > timedelta(0):
                index -= 1
            velocity = velocities.iloc[index]

        return numpy.array([velocity["x"], velocity["y"], velocity["z"]])

    def location_at_time(self, time: Union[datetime, timedelta]) -> numpy.ndarray:
        try:
            time = typepigeon.convert_value(time, timedelta)
        except TypeError:
            time = typepigeon.convert_value(time, datetime) - self.start.time
        velocities = self.__velocities
        if time >= timedelta(0):
            velocities = velocities.loc[
                (velocities.index >= timedelta(seconds=0)) & (velocities.index <= time)
            ]
        else:
            velocities = velocities.loc[
                (velocities.index <= timedelta(seconds=0)) & (velocities.index >= time)
            ]
        seconds = numpy.diff(
            numpy.concatenate(
                [
                    velocities.index.to_numpy(dtype="timedelta64[s]"),
                    numpy.expand_dims(
                        numpy.array(time, dtype="timedelta64[s]"), axis=0
                    ),
                ]
            )
        )
        return self.start.location + numpy.sum(
            velocities.to_numpy() * seconds[:, None].astype(float), axis=0
        ).astype(float)

    def distance(self, other: "SpatioTemporal", time: float) -> float:
        pass

    def relative_to(self, other: "SpatioTemporal") -> "SpatioTemporal":
        instance = self.start - other.start
        instance = SpatioTemporal(
            starting_location=instance.location,
            starting_velocity=instance.velocity,
            starting_time=instance.time,
        )

        for time, velocity in self.velocities.iterrows():
            instance.add_velocity_change(time=time, velocity=velocity)

        for time, event in self.events.iterrows():
            instance.add_event(
                time=time,
                name=event["name"],
                propagation_speed=event["propagation_speed"],
            )

        return instance

    def plot(self, dimension: int = None, axis: Axis = None, show: bool = False):
        if dimension is None:
            dimension = 0
        elif isinstance(dimension, str):
            dimensions = {
                "x": 0,
                "y": 1,
                "z": 2,
            }
            dimension = dimensions[dimension]
        if axis is None:
            axis = pyplot.figure().add_subplot(1, 1, 1)

        locations = self.locations.values[:, dimension]
        points = numpy.stack([locations, self.times], axis=1)
        handle = axis.scatter(points[:, 0], points[:, 1], label=self.name)
        points = points.reshape(-1, 1, 2)
        segments = numpy.concatenate([points[:-1], points[1:]], axis=1)
        line_collection = LineCollection(segments, linestyles="--")
        axis.add_collection(line_collection)

        if show:
            pyplot.show()

        return handle
