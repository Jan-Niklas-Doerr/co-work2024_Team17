import numpy as np

from solution import Solution


class Problem:

    def __init__(self, instance):
        self.problem_id = instance['instance_name']
        self.couriers = instance['couriers']
        self.deliveries = sorted(instance['deliveries'], key=lambda x: x.time_window_start)
        self.map_deliveries = {delivery.delivery_id: delivery for delivery in self.deliveries}
        self.number_of_couriers = len(self.couriers)
        self.number_of_deliveries = len(self.deliveries)
        self.travel_times = np.delete(np.array(instance['travel_time'][1:], dtype=int), 0, 1)
        self.solution = Solution(self)