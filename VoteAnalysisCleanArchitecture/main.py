import enum
import sys

from Entities.n_module import NModule, input_num
from UseCases.vote_algorithm import VoteAlgorithm
from InterfaceAdapters.nmodule_repository import NModuleRepository
from InterfaceAdapters.vote_algorithm_repository import VoteAlgorithmRepository
from UseCases.data_generator import generate_experiment_data


class MenuOption(enum.Enum):
    ADD_MODULE = 1
    LOAD_MODULE = 2
    SAVE_MODULE = 3
    SHOW_MODULES = 4
    SET_CURRENT_MODULE = 5
    SHOW_CURRENT_MODULE = 6
    ADD_VERSIONS = 7
    LOAD_MODULE_WITH_VERSIONS = 8
    SAVE_MODULE_WITH_VERSIONS = 9
    SHOW_MODULE_VERSIONS = 10
    GENERATE_EXPERIMENT_DATA = 11
    SAVE_EXPERIMENT_DATA = 12
    LOAD_EXPERIMENT_DATA = 13
    ADD_VOTE_ALGORITHM = 14
    LOAD_VOTE_ALGORITHMS = 15
    SAVE_VOTE_ALGORITHMS = 16
    SHOW_VOTE_ALGORITHMS = 17
    RUN_VOTE_ALGORITHMS = 18
    MAKE_EXPERIMENT_ANALYSIS = 19
    EXIT = 0


def display_menu():
    print('\nMenu:')
    print(f'{MenuOption.ADD_MODULE.value}. Add module to list')
    print(f'{MenuOption.LOAD_MODULE.value}. Load module list from DB')
    print(f'{MenuOption.SAVE_MODULE.value}. Save module to DB')
    print(f'{MenuOption.SHOW_MODULES.value}. Show modules list')
    print(f'{MenuOption.SET_CURRENT_MODULE.value}. Set current module')
    print(f'{MenuOption.SHOW_CURRENT_MODULE.value}. Show current module')
    print(f'{MenuOption.ADD_VERSIONS.value}. Add versions to module')
    print(f'{MenuOption.LOAD_MODULE_WITH_VERSIONS.value}. Load module with versions from DB')
    print(f'{MenuOption.SAVE_MODULE_WITH_VERSIONS.value}. Save module with versions to DB')
    print(f'{MenuOption.SHOW_MODULE_VERSIONS.value}. Show module versions')
    print(f'{MenuOption.GENERATE_EXPERIMENT_DATA.value}. Generate experiment data for module')
    print(f'{MenuOption.SAVE_EXPERIMENT_DATA.value}. Save module experiment data to DB')
    print(f'{MenuOption.LOAD_EXPERIMENT_DATA.value}. Load module experiment data from DB')
    print(f'{MenuOption.ADD_VOTE_ALGORITHM.value}. Add vote algorithm')
    print(f'{MenuOption.LOAD_VOTE_ALGORITHMS.value}. Load vote algorithms')
    print(f'{MenuOption.SAVE_VOTE_ALGORITHMS.value}. Save vote algorithms list')
    print(f'{MenuOption.SHOW_VOTE_ALGORITHMS.value}. Show vote algorithms')
    print(f'{MenuOption.RUN_VOTE_ALGORITHMS.value}. Run vote algorithms')
    print(f'{MenuOption.MAKE_EXPERIMENT_ANALYSIS.value}. Make experiment analysis')
    print(f'{MenuOption.EXIT.value}. Exit\n')


def get_choice():
    display_menu()
    choice = input_num("Please choice menu item: ",
                       (0, 19), int, True, 0)
    return MenuOption(choice)


def show_list(lst: list[tuple], header='List items:'):
    print('\n' + header)
    for i in range(len(lst)):
        print(f'{i + 1}. {str(lst[i])}')
    print('\n')


def check_var_is_not_none(var: any, err_str: str = 'Variable is None') -> bool:
    if var is not None:
        return True
    print(err_str)
    return False


def add_module(modules_list: list):
    default_module_name = f'Module {len(modules_list) + 1}'
    new_module_name = input(
        f'Enter module name [{default_module_name}]: ')
    if new_module_name == '' or new_module_name is None:
        new_module_name = default_module_name
    new_module_round_digits = input_num(
        'Enter number of module digits round: ', (0, float('inf')),
        int, True)
    new_model_min_generated_val = input_num(
        'Enter minimal value that can be generated by versions: ',
        (0, float('inf')), float, False, new_module_round_digits)
    new_model_max_generated_val = input_num(
        'Enter maximal value that can be generated by versions: ',
        (0, float('inf')), float, False, new_module_round_digits)
    module = NModule(
        new_module_name, new_module_round_digits,
        new_model_min_generated_val, new_model_max_generated_val)
    modules_list.append(module)
    print(f'Module "{module.name}" was successfully added to the list!')


def save_module_to_db(modules_list: list, current_module_index: int):
    if len(modules_list) > 0:
        if current_module_index is None:
            show_list(modules_list)
            current_module_index = input_num(
                'Enter module order number to save it: ',
                (1, len(modules_list)), int, True) - 1
        module_rep = NModuleRepository(modules_list[current_module_index])
        module_rep.save_module()
    else:
        print('Modules list is empty. There is no data to save!')


def set_current_module_index(modules_list: list) -> int:
    current_module_index = None
    if len(modules_list) > 0:
        show_list(modules_list)
        current_module_index = input_num(
            'Enter module order number to select it as a current module: ',
            (1, len(modules_list)), int, True) - 1
        print(f'Current module index is {current_module_index + 1}')
    else:
        print('Modules list is empty.')
    return current_module_index


def generate_data(modules_list: list, current_module_index: int, experiments_names_list: list):
    exp_name = input('Enter experiment name: ')
    generate_data = generate_experiment_data(
        modules_list[current_module_index],
        input_num('Enter iterations amount: ',
                  (0.0, float('inf'))), exp_name)
    if generate_data is not None:
        print('Experiment data was generated successfully!')
        experiments_names_list.append(exp_name)
    else:
        print('Error occurs during experiment data generation.')


def load_experiment_data(modules_list: list, current_module_index: int, experiments_names_list: list):
    module_rep = NModuleRepository(modules_list[current_module_index])
    if len(experiments_names_list) == 0:
        print('I am loading experiments names from DB. It can take several minutes...')
        experiments_names_list = module_rep.get_experiments_names()
    show_list(experiments_names_list, 'Experiments names:')
    exp_name_index = input_num(
        'Choice experiment by order number to its data load: ',
        (-1, len(modules_list) + 1)) - 1
    try:
        module_rep.load_experiment_data(experiments_names_list[exp_name_index])
    except ValueError:
        print('There is no module name to load!')
    except Exception:
        print('Something is wrong!')


def add_vote_algorithm(vote_algorithms_list: list):
    algorithm_name = input('Enter vote algorithm name: ')
    module_name = input('Enter python module name (it should located in '
                        'VoteAlgorithms package): ')
    vote_function_name = input('Enter vote function name in module: ')
    vote_algorithms_list.append(
        VoteAlgorithm(algorithm_name, vote_function_name, module_name))


def run_vote_algorithm(modules_list: list, current_module_index: int,
                       vote_algorithms_list: list):
    if len(modules_list[current_module_index].global_results_lst) > 0:
        if check_var_is_not_none(current_module_index, ""):
            if len(vote_algorithms_list) > 0:
                for cur_algorithm in vote_algorithms_list:
                    cur_algorithm.vote(
                        modules_list[current_module_index].global_results_lst)
                    cur_algorithm_rep = VoteAlgorithmRepository(cur_algorithm)
                    cur_algorithm_rep.save_vote_results()
            else:
                print('There are no algorithms to show!')
        else:
            print('Current module does not save in DB! Save all necessary '
                  'data before running algorithms')
    else:
        print('There is no experiment data list. Please generate it before '
              'run voting!')


def main():
    module_index_err_str = 'Current module index is not defined yet. Please set it before using this menu item.'
    modules_list = []
    current_module_index: int = None
    vote_algorithms_list = []
    experiments_names_list = []

    while (user_chosen_item := get_choice()) != MenuOption.EXIT:
        if user_chosen_item == MenuOption.ADD_MODULE:
            add_module(modules_list)
        elif user_chosen_item == MenuOption.LOAD_MODULE:
            modules_list.append(NModuleRepository(NModule('NoName', 6)).load_module())
        elif user_chosen_item == MenuOption.SAVE_MODULE:
            save_module_to_db(modules_list, current_module_index)
        elif user_chosen_item == MenuOption.SHOW_MODULES:
            if len(modules_list) > 0:
                show_list(modules_list)
            else:
                print('Modules list is empty.')
        elif user_chosen_item == MenuOption.SET_CURRENT_MODULE:
            current_module_index = set_current_module_index(modules_list)
        elif user_chosen_item == MenuOption.SHOW_CURRENT_MODULE:
            if check_var_is_not_none(current_module_index, module_index_err_str):
                print(f'{current_module_index}. {str(modules_list[current_module_index])}')
        elif user_chosen_item == MenuOption.ADD_VERSIONS:
            if check_var_is_not_none(current_module_index, module_index_err_str):
                modules_list[current_module_index].add_versions()
        elif user_chosen_item == MenuOption.LOAD_MODULE_WITH_VERSIONS:
            if check_var_is_not_none(current_module_index, ""):
                modules_list[current_module_index] = NModuleRepository(modules_list[current_module_index]).load_module_with_versions()
            else:
                modules_list.append(NModuleRepository(NModule('NoName', 6)).load_module_with_versions())
        elif user_chosen_item == MenuOption.SAVE_MODULE_WITH_VERSIONS:
            if check_var_is_not_none(current_module_index, module_index_err_str):
                NModuleRepository(modules_list[current_module_index]).save_module_with_versions()
        elif user_chosen_item == MenuOption.SHOW_MODULE_VERSIONS:
            if check_var_is_not_none(current_module_index, module_index_err_str):
                if len(modules_list[current_module_index].versions_list) > 0:
                    show_list(modules_list[current_module_index].versions_list,
                              f'Versions of {current_module_index + 1} module:')
                else:
                    print(f'No versions for {current_module_index + 1} module found')
        elif user_chosen_item == MenuOption.GENERATE_EXPERIMENT_DATA:
            if check_var_is_not_none(current_module_index, module_index_err_str):
                generate_data(modules_list, current_module_index, experiments_names_list)
        elif user_chosen_item == MenuOption.SAVE_EXPERIMENT_DATA:
            if check_var_is_not_none(current_module_index, module_index_err_str):
                NModuleRepository(modules_list[current_module_index]).save_experiment_data()
        elif user_chosen_item == MenuOption.LOAD_EXPERIMENT_DATA:
            if check_var_is_not_none(current_module_index, module_index_err_str):
                load_experiment_data(modules_list, current_module_index, experiments_names_list)
        elif user_chosen_item == MenuOption.ADD_VOTE_ALGORITHM:
            add_vote_algorithm(vote_algorithms_list)
        elif user_chosen_item == MenuOption.LOAD_VOTE_ALGORITHMS:
            usr_answer = input('Unsaved algorithms will be lost! Are you '
                               'sure (Y - yes; any key - no)? ')
            if usr_answer.upper() == 'Y':
                vote_algorithms_list = VoteAlgorithmRepository(None).load_algorithms()
        elif user_chosen_item == MenuOption.SAVE_VOTE_ALGORITHMS:
            if len(vote_algorithms_list) > 0:
                for cur_algorithm in vote_algorithms_list:
                    VoteAlgorithmRepository(cur_algorithm).save_vote_algorithm()
            else:
                print('There are no algorithms to save!')
        elif user_chosen_item == MenuOption.SHOW_VOTE_ALGORITHMS:
            if len(vote_algorithms_list) > 0:
                for cur_algorithm in vote_algorithms_list:
                    print(f'{cur_algorithm}')
            else:
                print('There are no algorithms to show!')
        elif user_chosen_item == MenuOption.RUN_VOTE_ALGORITHMS:
            run_vote_algorithm(modules_list, current_module_index, vote_algorithms_list)
        elif user_chosen_item == MenuOption.MAKE_EXPERIMENT_ANALYSIS:
            pass


if __name__ == '__main__':
    sys.exit(main())
