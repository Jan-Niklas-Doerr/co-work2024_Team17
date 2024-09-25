import pathlib

from problem import Problem
import read_data
import feasibility_checker

# path to the folder training_data

# type_of_instance = 'training_data'
type_of_instance = 'playground'

instance_folder = pathlib.Path(__file__).parent.parent / type_of_instance
solution_folder = pathlib.Path(__file__).parent.parent / 'solutions'

all_instances = read_data.process_all_instances(instance_folder)

for instance in all_instances:
    problem = Problem(instance)
    # print(problem.deliveries)
    # print(problem.couriers)
    # print(problem.travel_times)
    # print(problem.solution.routes)
    # print(problem.solution.objective)
    # print(problem.solution.eval())
    # print(problem.solution.eval())
    # problem.solution.save_to_csv(solution_folder)
    # print(sum([1 for i in problem.solution.routes.values() if len(i) == 2]))
    # print(sum([1 for i in problem.solution.routes.values() if len(i) > 2]))

    sorted_id = [x for x in sorted(problem.deliveries, key=lambda x: x.pickup_stacking_id)]

    # only show first set of identical pickup stacking id with more than one

    for i, sid in enumerate(sorted_id):
        if i == len(sorted_id)-1:
            break
        if sorted_id[i+1].pickup_stacking_id == sid.pickup_stacking_id:
            print(sid)
            print(sorted_id[i+1])

            break



    sorted_id = []


# print([[len(i["couriers"]), len(i['deliveries'])] for i in all_instances])

# check for feasibility
# feasibility_checker.check_feasibility_files(instance_folder, solution_folder)