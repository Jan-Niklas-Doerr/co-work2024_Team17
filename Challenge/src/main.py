import pathlib

from problem import Problem
import read_data

# path to the folder training_data

# type_of_instance = 'training_data'
type_of_instance = 'playground'

instance_folder = pathlib.Path(__file__).parent.parent / type_of_instance

all_instances = read_data.process_all_instances(instance_folder)

for instance in all_instances:
    problem = Problem(instance)
    # print(problem.deliveries)
    # print(problem.couriers)
    # print(problem.travel_times)
    # print(problem.solution.routes)
    print(problem.solution.objective)
    print(problem.solution.eval())
    print(problem.solution.eval())

# print([[len(i["couriers"]), len(i['deliveries'])] for i in all_instances])