import pathlib

from problem import Problem
import read_data
import feasibility_checker

# path to the folder training_data

# type_of_instance = 'training_data'
# type_of_instance = 'training_data_hard'
type_of_instance = 'final_test_set'

instance_folder = pathlib.Path(__file__).parent.parent / type_of_instance
solution_folder = pathlib.Path(__file__).parent.parent / 'solutions'

all_instances = read_data.process_all_instances(instance_folder)

count = 0

for instance in all_instances:
    problem = Problem(instance)
    print(f'problem has {problem.number_of_couriers} couriers and {problem.number_of_deliveries} deliveries')
    # print(problem.couriers)
    # print(problem.travel_times)
    # print(problem.solution.routes)
    print(problem.solution.objective)
    # problem.solution.improve_matching(N=1000)
    
    problem.solution.improve_matching(N=500)
    a = problem.solution.eval()
    if not a[2]:
        print('solution is infeasible')
        count += 1


    # print(problem.solution.eval())
    problem.solution.save_to_csv(solution_folder)
    # print(sum([1 for i in problem.solution.routes.values() if len(i) == 2]))
    # print(sum([1 for i in problem.solution.routes.values() if len(i) > 2]))

print(f'Number of infeasible solutions: {count}')
# print([[len(i["couriers"]), len(i['deliveries'])] for i in all_instances])

# check for feasibility
# feasibility_checker.check_feasibility_files(instance_folder, solution_folder)