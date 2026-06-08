from utils.actor_templates.uav_template import make_uav_protocol
from utils.viz_templates.uav_viz_template import UAVVizMixin
from utils.common.config import CLUSTER_WAYPOINTS, NUM_UAVS


def make_uav(cluster_index: int) -> type:
    """
    Factory that returns a UAV protocol class for the given cluster slot.

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
    return make_uav_protocol(
        waypoints     = CLUSTER_WAYPOINTS,
        cluster_index = cluster_index,
        num_uavs      = NUM_UAVS,
    )


def make_uav_viz(cluster_index: int) -> type:
    """
    Same as make_uav() but with GrADySim visualisation support mixed in.
    Use this class with VisualizationHandler enabled.
    """
    class _UAVViz(UAVVizMixin, make_uav_protocol(
        waypoints     = CLUSTER_WAYPOINTS,
        cluster_index = cluster_index,
        num_uavs      = NUM_UAVS,
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