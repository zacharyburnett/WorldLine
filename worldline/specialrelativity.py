from datetime import datetime, timedelta
from typing import Optional, Tuple, Union

from matplotlib import pyplot
from matplotlib.axis import Axis
import numpy

from worldline.model import SpaceTimeLocation, SpatioTemporal


class RelativisticReferenceFrame(SpaceTimeLocation):
    c = 299792458

    def __init__(
        self,
        starting_location: Tuple[float, Optional[float], Optional[float]] = None,
        starting_time: Union[timedelta, datetime] = None,
    ):
        if starting_location is None:
            starting_location = 0

        SpaceTimeLocation.__init__(self, location=starting_location, time=starting_time)

        self.__objects = []
        self.__events = []

    @property
    def objects(self) -> [SpatioTemporal]:
        return self.__objects

    def add_object(
        self,
        spatiotemporal_object: SpatioTemporal,
    ):
        self.__objects.append(spatiotemporal_object.relative_to(self))

    def add_event(
        self,
        object_index: Union[int, str],
        start_time: Union[timedelta, datetime],
        event_name: str = None,
        propagation_speed: float = None,
    ):
        if propagation_speed is None:
            propagation_speed = self.c

        if isinstance(object_index, int):
            spatiotemporal_object = self.objects[object_index]
            spatiotemporal_object.add_event(
                time=start_time, name=event_name, propagation_speed=propagation_speed
            )
        else:
            for spatiotemporal_object in self.objects:
                if spatiotemporal_object.name == object_index:
                    spatiotemporal_object.add_event(
                        time=start_time,
                        name=event_name,
                        propagation_speed=propagation_speed,
                    )

    def plot(
        self, reference_lines: bool = False, axis: Axis = None, show: bool = False
    ):
        if axis is None:
            figure = pyplot.figure()
            axis = figure.add_subplot(1, 1, 1)

        handles = [
            spatiotemporal_object.plot(axis=axis)
            for spatiotemporal_object in self.objects
        ]

        if reference_lines:
            xlim = axis.get_xlim()
            ylim = axis.get_ylim()

            extreme = numpy.nanmax(numpy.abs([xlim, ylim]))
            axis.plot(
                [-extreme, extreme],
                [-extreme / self.c, extreme / self.c],
                "--k",
                alpha=0.3,
            )
            axis.plot(
                [-extreme, extreme],
                [extreme / self.c, -extreme / self.c],
                "--k",
                alpha=0.3,
            )

            axis.hlines([0], -extreme, extreme, "k", alpha=0.3)
            axis.vlines([0], -extreme, extreme, "k", linestyles="--", alpha=0.3)

            axis.set_xlim(xlim)
            axis.set_ylim(ylim)

        axis.legend(handles=handles, labels=[o.name for o in self.objects])

        if show:
            pyplot.show()
