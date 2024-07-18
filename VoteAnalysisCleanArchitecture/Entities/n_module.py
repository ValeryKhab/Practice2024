import json

from Entities.n_version import NVersion


def input_num(user_str='Please enter number', limit=(float('-inf'), float('inf')), target_type=int,
              included_borders=False, round_to=6):
    def is_within_limit(value):
        if included_borders:
            return limit[0] <= value <= limit[1]
        else:
            return limit[0] < value < limit[1]

    while True:
        try:
            user_input = input(user_str)
            user_num = target_type(user_input)
            if not is_within_limit(user_num):
                raise ValueError(f'Expected value from {limit[0]} to {limit[1]}')
        except ValueError as err:
            print('Entered value is incorrect! ' + str(err))
        except Exception as err:
            print('Unknown error! ' + str(err))
        else:
            return round(user_num, round_to)


class NModule:
    """
    N-version programming module
    """

    def __init__(self, name, round_to, min_out_val=100, max_out_val=1000):
        """
        NModule class constructor
        :param name: Module name
        :param round_to: Digits amount fallow after dot delimiter
        """
        self._id = None
        self.name = name
        self.round_to = round_to
        self.min_out_val = min_out_val
        self.max_out_val = max_out_val
        # Versions, which are included into module
        self._versions_list: list[NVersion] = []
        # List of tuples, that contain constant diversities values
        self._const_diversities_versions_list = []
        # List of tuples, that contain intervals to generate dynamic diversities
        self._dynamic_diversities_intervals_dict = dict()
        self._const_diversities_count = 0
        self._dynamic_diversities_count = 0
        self._global_results_lst: list = []
        self._global_results_lst_2_write: list[tuple] = []
        self._experiment_name = None

    @property
    def id(self):
        return self._id

    @property
    def versions_list(self):
        return self._versions_list

    @versions_list.setter
    def versions_list(self, new_ver_lst: list):
        self._versions_list = new_ver_lst

    @property
    def const_diversities_versions_list(self):
        return self._const_diversities_versions_list

    @const_diversities_versions_list.setter
    def const_diversities_versions_list(self, new_div_ver_lst: list):
        self._const_diversities_versions_list = new_div_ver_lst

    @property
    def dynamic_diversities_intervals_dict(self):
        return self._dynamic_diversities_intervals_dict

    @dynamic_diversities_intervals_dict.setter
    def dynamic_diversities_intervals_dict(self, new_dyn_div_intervals: list):
        self._dynamic_diversities_intervals_dict = new_dyn_div_intervals

    @property
    def const_diversities_count(self):
        return self._const_diversities_count

    @const_diversities_count.setter
    def const_diversities_count(self, const_div_count: int):
        self._const_diversities_count = const_div_count

    @property
    def dynamic_diversities_count(self):
        return self._dynamic_diversities_count

    @dynamic_diversities_count.setter
    def dynamic_diversities_count(self, dyn_div_count: int):
        self._dynamic_diversities_count = dyn_div_count

    @property
    def normed_connectivity_matrix(self):
        """
        Figure out distance length between versions in the metric space in percents (from 0 to 1)
        :return: matrix (tuple of tuples)
        """

        if not self._versions_list or len(self._versions_list) == 0:
            raise AttributeError('There are not versions in module')

        matrix = []
        for cur_ver in self._versions_list:
            matrix.append([cur_ver.calculate_distance_to(another_ver) for another_ver in self._versions_list])

        max_val = max(map(max, matrix))

        try:
            for i in range(len(matrix)):
                for j in range(len(matrix[i])):
                    matrix[i][j] /= max_val
        except ZeroDivisionError:
            print('Max distance between all versions is zero, so connectivity matrix cannot by normed')

        return tuple(map(tuple, matrix))

    @property
    def global_results_lst(self):
        return self._global_results_lst

    def _get_global_results_lst_2_write(self):
        for sub_lst in self._global_results_lst:
            for itm in sub_lst:
                self._global_results_lst_2_write.append(
                    (itm.version_id, itm.version_name, itm.version_reliability,
                     json.dumps({'version_coordinates': itm.version_common_coordinates}), itm.version_answer,
                     itm.correct_answer, itm.module_id, itm.module_name,
                     json.dumps({'connectivity_matrix': itm.module_connectivity_matrix}), itm.module_iteration_num,
                     itm.experiment_name)
                )

    @property
    def global_results_lst_2_write(self):
        if len(self._global_results_lst_2_write) == 0:
            self._get_global_results_lst_2_write()
        return self._global_results_lst_2_write

    def add_versions(self):
        while input('Add new version to module? Yes - any key; No - n. Your choice: ') != 'n':
            cur_new_version = NVersion()
            cur_new_version.name = input('Enter version name: ')

            if self._const_diversities_count < 1:
                self._const_diversities_count = input_num('Enter constant diversity metrics count: ', (0, float('inf')))
            if self._dynamic_diversities_count < 1:
                self._dynamic_diversities_count = input_num('Enter dynamic diversity metrics count: ',
                                                            (0, float('inf')))

            const_diversities_lst = []
            for i in range(self._const_diversities_count):
                const_diversities_lst.append(input_num(f'Enter {i + 1} diversity coordinate: ',
                                                       (float('-inf'), float('inf')),
                                                       float, self.round_to))
            cur_new_version.const_diversities = tuple(const_diversities_lst)
            self._const_diversities_versions_list.append(cur_new_version.const_diversities)

            tmp_dynamic_diversities_lst = []
            for i in range(self._dynamic_diversities_count):
                print(f'Enter limits (from min to max) to generate {i + 1} diversity coordinate')
                tmp_dynamic_diversities_lst.append(
                    (input_num('Min value: ', (float('-inf'), float('inf')), float, self.round_to),
                     input_num('Max value: ', (float('-inf'), float('inf')), float, self.round_to))
                )
            self._dynamic_diversities_intervals_dict[cur_new_version.name] = tmp_dynamic_diversities_lst

            cur_new_version.reliability = input_num('Reliability: ', (0, 1), float, True, self.round_to)
            cur_new_version.generate_dynamic_diversities(self._dynamic_diversities_intervals_dict[cur_new_version.name],
                                                         self.round_to)
            self._versions_list.append(cur_new_version)

    def __str__(self):
        res_str = f'id: {self._id}\tname: {self.name}\tround to: {self.round_to}\tdynamic diversities intervals: '
        res_str += f'{self._dynamic_diversities_intervals_dict}\tconst diversities count: '
        res_str += f'{self._const_diversities_count}\tdynamic diversities count: {self._dynamic_diversities_count}'
        return res_str
