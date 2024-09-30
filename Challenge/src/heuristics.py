import copy
import random

def two_opt_bwtn_couriers(solution, courier_ids, threshold = 0.3):
    new_solution = copy.deepcopy(solution)
    initial_obj = solution.objective_driver[courier_ids[0]] + solution.objective_driver[courier_ids[1]]
    for i in range(len(new_solution.routes[courier_ids[0]])):
        for j in range(len(new_solution.routes[courier_ids[1]])):

            new_solution.routes[courier_ids[0]] = new_solution.routes[courier_ids[0]][:i] + new_solution.routes[courier_ids[1]][j:]
            new_solution.routes[courier_ids[1]] = new_solution.routes[courier_ids[1]][:j] + new_solution.routes[courier_ids[0]][i:]

            # repair by searching for entries that only appear once in the route
            faulties = []
            for delivery_id in new_solution.routes[courier_ids[0]]:
                if new_solution.routes[courier_ids[0]].count(delivery_id) == 1:
                    faulties.append(delivery_id)

            # replace on fauty entry by the one that is missing
            if len(faulties) % 2 != 0:
                new_solution.routes[courier_ids[0]].remove(faulties[0])
                new_solution.routes[courier_ids[1]].append(faulties[0])
            if len(faulties) != 0:
                for i in range(int(len(faulties)/2)):
                    new_solution.routes[courier_ids[0]] = list(map(lambda x: x.replace(faulties[i*2], faulties[i*2+1]), new_solution.routes[courier_ids[0]]))
                    new_solution.routes[courier_ids[1]] = list(map(lambda x: x.replace(faulties[i*2+1], faulties[i*2]), new_solution.routes[courier_ids[1]]))

            obj, driver_dict, feasible = new_solution.eval(selected_couriers=courier_ids)
            if feasible and obj < initial_obj:
                new_solution.objective += obj - initial_obj
                new_solution.objective_driver[courier_ids[0]] = driver_dict[courier_ids[0]]
                new_solution.objective_driver[courier_ids[1]] = driver_dict[courier_ids[1]]
                solution = new_solution
                return True
    if random.random() < threshold:
        solution = new_solution
    return False

def n_opt_route(solution, courier_id, arity):
    new_solution = copy.deepcopy(solution)
    tour = new_solution.routes[courier_id]
    initial_obj = solution.objective_driver[courier_id]

    for i in range(1, len(tour) - 1):
        for j in range(i + 1, len(tour)):
            if arity == 1:
                tour = tour[:i] + tour[i+1:j] + [tour[i]] + tour[j:]
            elif arity == 2:
                tmp = tour[i]
                tour[i] = tour[j]
                tour[j] = tmp  
            
            # calc savings and check if feasible
            obj, driver_dict, feasible = new_solution.eval(selected_couriers=[courier_id])
            if feasible and obj < initial_obj:
                new_solution.objective += obj - initial_obj
                new_solution.objective_driver[courier_id] = driver_dict[courier_id]
                solution = new_solution
                return True
    return False

    

