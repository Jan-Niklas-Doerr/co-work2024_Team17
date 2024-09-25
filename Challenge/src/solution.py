import copy
import csv
import random
import warnings

from heuristics import n_opt_route

class Solution:
    def __init__(self, problem):
        self.problem = problem
        self.routes, self.objective_driver, self.objective, self.feasible = self.construction_heuristic()

    def eval(self, selected_couriers=None):
        """ evaluate the objective function of the solution, return float('inf') if infeasible """
        
        orderd = set([i.delivery_id for i in self.problem.deliveries])
        delivered = set([i for sublist in self.routes.values() for i in sublist])
        if orderd != delivered:
            return (float('inf'), {}, False)
        
        obj = 0
        obj_driver = {i.courier_id : 0 for i in self.problem.couriers}

        iterate_over = self.problem.couriers if selected_couriers is None else [i for i in self.problem.couriers if i.courier_id in selected_couriers]

        for courier in iterate_over:
            time = 0
            loc = int(courier.location)
            capacity = int(courier.capacity)

            picked_up = {delivery_id: False for delivery_id in self.routes[courier.courier_id]}
            delivered = {delivery_id: False for delivery_id in self.routes[courier.courier_id]}

            if len(picked_up) > 4:
                return (float('inf'), {'error': 'too many orders', 'courier': courier.courier_id}, False)
            for delivery_id in self.routes[courier.courier_id]:
                delivery = self.problem.map_deliveries[delivery_id]
                if not picked_up[delivery_id]:
                    time = max(time + self.problem.travel_times[loc-1][delivery.pickup_loc-1], delivery.time_window_start)
                    picked_up[delivery_id] = True
                    loc = delivery.pickup_loc
                    capacity -= delivery.capacity
                    if capacity < 0:
                        return (float('inf'), {'error': 'capacity exceeded', 'courier': courier.courier_id}, False)
                else:
                    delivered[delivery_id] = True
                    time += self.problem.travel_times[loc-1][delivery.dropoff_loc-1]
                    obj += time
                    obj_driver[courier.courier_id] += time
                    loc = delivery.dropoff_loc
                    capacity += delivery.capacity

            if time > 180:
                return (float('inf'), {'error': 'max working time exceeded', 'courier': courier.courier_id}, False)
            if any([not delivered[delivery_id] for delivery_id in self.routes[courier.courier_id]]):
                return (float('inf'), {'error': 'not all orders delivered', 'courier': courier.courier_id}, False)

        return (obj, obj_driver, True)

    def construction_heuristic(self):
        """ construction of initial solution via greedy insertion and without stacking"""  # TODO replace by better method

        routes = {i.courier_id : [] for i in self.problem.couriers}
        times = {i.courier_id : 0 for i in self.problem.couriers}
        obj_driver = {i.courier_id : 0 for i in self.problem.couriers}
        loc = {i.courier_id : i.location for i in self.problem.couriers}
        objective = 0
        feasible = True

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

            if driver_selected is None:
                # no feasible assigment found
                feasible = False
                warnings.warn(f"no feasible assignment found for delivery {delivery.delivery_id}, random assigment. infeasible solution")
                driver_selected = random.choice(list(self.problem.couriers)).courier_id
                routes[driver_selected].append(delivery.delivery_id)
                routes[driver_selected].append(delivery.delivery_id)
                obj_increase = max(times[driver_selected] + self.problem.travel_times[loc[driver_selected]-1][delivery.pickup_loc-1],
                                delivery.time_window_start) \
                                + self.problem.travel_times[delivery.pickup_loc-1][delivery.dropoff_loc-1]
                objective += obj_increase
                obj_driver[driver_selected] += obj_increase
                times[driver_selected] = obj_increase
                loc[driver_selected] = delivery.dropoff_loc
            else:
                routes[driver_selected].append(delivery.delivery_id)
                routes[driver_selected].append(delivery.delivery_id)
                objective += obj_increase
                obj_driver[driver_selected] += obj_increase
                times[driver_selected] = obj_increase
                loc[driver_selected] = delivery.dropoff_loc
        return routes, obj_driver, objective, feasible
    
    def improve_tours(self):
        for courier_id in self.routes.keys():
            imp_pos = True
            while(imp_pos):
                imp_pos = n_opt_route(self, courier_id, 1)
    
    def save_to_csv(self, path):
        """ save the solution to a csv file """

        with open(f"{path}/{self.problem.problem_id}.csv", 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['ID'])
            for courier_id, deliveries in self.routes.items():
                writer.writerow([courier_id] + deliveries)