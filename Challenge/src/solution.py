import copy
import csv

class Solution:
    def __init__(self, problem):
        self.problem = problem
        self.routes, self.objective = self.construction_heuristic()

    def eval(self):
        """ evaluate the objective function of the solution, return float('inf') if infeasible """
        
        orderd = set([i.delivery_id for i in self.problem.deliveries])
        delivered = set([i for sublist in self.routes.values() for i in sublist])
        if orderd != delivered:
            return (float('inf'), False)
        
        obj = 0
        for courier in self.problem.couriers:
            time = 0
            loc = int(courier.location)
            capacity = int(courier.capacity)

            picked_up = {delivery_id: False for delivery_id in self.routes[courier.courier_id]}
            if len(picked_up) > 4:
                return (float('inf'), False)
            for delivery_id in self.routes[courier.courier_id]:
                delivery = self.problem.map_deliveries[delivery_id]
                if not picked_up[delivery_id]:
                    time = max(time + self.problem.travel_times[loc-1][delivery.pickup_loc-1], delivery.time_window_start)
                    picked_up[delivery_id] = True
                    loc = delivery.pickup_loc
                    capacity -= delivery.capacity
                    if capacity < 0:
                        return (float('inf'), False)
                else:
                    time += self.problem.travel_times[loc-1][delivery.dropoff_loc-1]
                    obj += time
                    loc = delivery.dropoff_loc
                    capacity += delivery.capacity

            if time > 180:
                return (float('inf'), False)
            if any([not picked_up[delivery_id] for delivery_id in self.routes[courier.courier_id]]):
                return (float('inf'), False)

        return (obj, True)

    def construction_heuristic(self):
        """ construction of initial solution via greedy insertion and without stacking"""  # TODO replace by better method

        routes = {i.courier_id : [] for i in self.problem.couriers}
        times = {i.courier_id : 0 for i in self.problem.couriers}
        loc = {i.courier_id : i.location for i in self.problem.couriers}
        objective = 0

        for delivery in self.problem.deliveries:
            obj_increase = float('inf')
            driver_selected = None
            for courier in self.problem.couriers:
                c_id = courier.courier_id
                if delivery.capacity > courier.capacity:
                    continue
                if len(routes[c_id]) == 4:
                    continue
                else:
                    tmp_increase = max(times[c_id] + self.problem.travel_times[loc[c_id]-1][delivery.pickup_loc-1],
                                        delivery.time_window_start) \
                                        + self.problem.travel_times[delivery.pickup_loc-1][delivery.dropoff_loc-1]
                    
                    if tmp_increase < obj_increase and tmp_increase <= 180:
                        obj_increase = tmp_increase
                        driver_selected = c_id

            routes[driver_selected].append(delivery.delivery_id)
            routes[driver_selected].append(delivery.delivery_id)
            objective += obj_increase
            times[driver_selected] = obj_increase
            loc[driver_selected] = delivery.dropoff_loc
        return routes, objective
    
    def save_to_csv(self, path):
        """ save the solution to a csv file """

        with open(f"{path}/{self.problem.problem_id}.csv", 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['ID'])
            for courier_id, deliveries in self.routes.items():
                writer.writerow([courier_id] + deliveries)