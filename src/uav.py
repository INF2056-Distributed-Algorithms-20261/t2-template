from typing import List, Tuple

from utils.actor_templates.uav_template import make_uav_protocol
from utils.viz_templates.uav_viz_template import UAVVizMixin
from utils.common.config import CLUSTER_WAYPOINTS, NUM_UAVS


def make_uav(
    cluster_index: int,
    waypoints: List[Tuple[float, float, float]] = None,
    group_size: int = None,
) -> type:
    """
    Factory that returns a UAV protocol class for the given cluster slot.

    Args:
        cluster_index: This UAV's slot within its sub-group (0-based).
        waypoints:     Ordered waypoint path for this UAV's group.
                       Defaults to CLUSTER_WAYPOINTS.
        group_size:    Number of UAVs sharing this path (used for
                       formation spacing).  Defaults to NUM_UAVS.

    If you want to add behaviours to every UAV (e.g. battery drain, swap
    logic), do it here: add a mixin before make_uav_protocol, or subclass
    the returned class.

    Example — adding battery drain to every UAV:

        class BatteryMixin:
            def handle_telemetry(self, telemetry):
                super().handle_telemetry(telemetry)
                # compute distance moved, subtract from self.battery …

        class _UAV(BatteryMixin, UAVVizMixin, make_uav_protocol(
            waypoints     = CLUSTER_WAYPOINTS,
            cluster_index = cluster_index,
            num_uavs      = NUM_UAVS,
        )):
            pass
        return _UAV
    """
    if waypoints is None:
        waypoints = CLUSTER_WAYPOINTS
    if group_size is None:
        group_size = NUM_UAVS

    return make_uav_protocol(
        waypoints     = waypoints,
        cluster_index = cluster_index,
        num_uavs      = group_size,
    )


def make_uav_viz(
    cluster_index: int,
    waypoints: List[Tuple[float, float, float]] = None,
    group_size: int = None,
) -> type:
    """
    Same as make_uav() but with GrADySim visualisation support mixed in.
    Use this class with VisualizationHandler enabled.

    Args:
        cluster_index: This UAV's slot within its sub-group (0-based).
        waypoints:     Ordered waypoint path for this UAV's group.
                       Defaults to CLUSTER_WAYPOINTS.
        group_size:    Number of UAVs sharing this path (used for
                       formation spacing).  Defaults to NUM_UAVS.
    """
    if waypoints is None:
        waypoints = CLUSTER_WAYPOINTS
    if group_size is None:
        group_size = NUM_UAVS

    class _UAVViz(UAVVizMixin, make_uav_protocol(
        waypoints     = waypoints,
        cluster_index = cluster_index,
        num_uavs      = group_size,
    )):
        """
        Example UAV Protocol with added Visualization support.
        If you want to implement your own variation of the protocol,
        add stuff to this class or create another class that inherits
        from make_uav_protocol(...) and UAVVizMixin and mix in other
        behaviors you want.
        """
        pass

    _UAVViz.__name__ = f"UAV_slot{cluster_index}"
    return _UAVViz