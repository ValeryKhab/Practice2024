from random import random, normalvariate, uniform
from VoteAnalysisCleanArchitecture.Entities.n_result import NResult
from VoteAnalysisCleanArchitecture.Entities.n_module import NModule


class DataGenerator:
    def __init__(self, module: NModule):
        self.module = module

    def group_versions(self):
        clone_versions = set()
        similar_versions = set()
        partly_similar_versions = set()
        difference_versions = set()
        for j in range(len(self.module.versions_list)):
            for k in range(len(self.module.versions_list)):
                if k > j:
                    if (
                        0
                        <= self.module.normed_connectivity_matrix[j][k]
                        <= 0.05
                    ):
                        self.add_to_set(clone_versions, j, k)
                    elif (
                        0.05
                        < self.module.normed_connectivity_matrix[j][k]
                        < 0.4
                    ):
                        self.add_to_set(similar_versions, j, k)
                    elif (
                        0.4
                        <= self.module.normed_connectivity_matrix[j][k]
                        <= 0.6
                    ):
                        self.add_to_set(partly_similar_versions, j, k)
                    else:
                        self.add_to_set(difference_versions, j, k)
        return (
            clone_versions,
            similar_versions,
            partly_similar_versions,
            difference_versions,
        )

    def add_to_set(self, version_set, j, k):
        if self.module.versions_list[j] not in version_set:
            version_set.add(self.module.versions_list[j])
        if self.module.versions_list[k] not in version_set:
            version_set.add(self.module.versions_list[k])

    def create_result(
        self, ver, v_answer, cur_correct_val, i, experiment_name
    ):
        return NResult(
            v_id=ver.id,
            v_name=ver.name,
            v_reliability=ver.reliability,
            v_common_coordinates=ver.common_coordinates_list,
            v_answer=v_answer,
            c_answer=cur_correct_val,
            m_id=self.module.id,
            m_name=self.module.name,
            m_connectivity_matrix=self.module.normed_connectivity_matrix,
            m_iteration_num=i,
            version=ver,
            experiment_name=experiment_name,
        )

    def generate_error_value(self, base_val, diversity_coefficient):
        return round(
            normalvariate(base_val, diversity_coefficient * base_val),
            self.module.round_to,
        )

    def process_clone_versions(
        self, clone_versions, cur_correct_val, result_lst, i, experiment_name
    ):
        try:
            min_rel = min(ver.reliability for ver in clone_versions)
        except ValueError:
            min_rel = 1

        cur_clone_reliability = random()

        for ver in clone_versions:
            if cur_clone_reliability <= min_rel:
                result_lst.append(
                    self.create_result(
                        ver,
                        cur_correct_val,
                        cur_correct_val,
                        i,
                        experiment_name,
                    )
                )
            else:
                clone_error_val = round(
                    uniform(self.module.min_out_val, self.module.max_out_val),
                    self.module.round_to,
                )
                result_lst.append(
                    self.create_result(
                        ver,
                        clone_error_val,
                        cur_correct_val,
                        i,
                        experiment_name,
                    )
                )

    def process_similar_versions(
        self, similar_versions, cur_correct_val, result_lst, i, experiment_name
    ):
        cur_similar_reliability = random()
        correct_similar_versions = {
            ver
            for ver in similar_versions
            if cur_similar_reliability <= ver.reliability
        }
        similar_base_error_val = (
            cur_correct_val
            if correct_similar_versions
            else round(
                uniform(self.module.min_out_val, self.module.max_out_val),
                self.module.round_to,
            )
        )
        diversity_coefficient = round(
            uniform(0.06, 0.39), self.module.round_to
        )

        for ver in similar_versions:
            if cur_similar_reliability > ver.reliability:
                similar_error_val = self.generate_error_value(
                    similar_base_error_val, diversity_coefficient
                )
                result_lst.append(
                    self.create_result(
                        ver,
                        similar_error_val,
                        cur_correct_val,
                        i,
                        experiment_name,
                    )
                )
            else:
                result_lst.append(
                    self.create_result(
                        ver,
                        cur_correct_val,
                        cur_correct_val,
                        i,
                        experiment_name,
                    )
                )

    def process_partly_similar_versions(
        self,
        partly_similar_versions,
        cur_correct_val,
        result_lst,
        i,
        experiment_name,
    ):
        cur_partly_similar_diversity = random()
        partly_similar_depended_versions = set()
        partly_similar_independent_versions = set()

        for ver1 in partly_similar_versions:
            for ver2 in partly_similar_versions:
                if ver1 != ver2:
                    v1_index = self.module.versions_list.index(ver1)
                    v2_index = self.module.versions_list.index(ver2)
                    if (
                        self.module.normed_connectivity_matrix[v1_index][
                            v2_index
                        ]
                        >= cur_partly_similar_diversity
                    ):
                        partly_similar_depended_versions.add(ver1)
                        partly_similar_depended_versions.add(ver2)
                    else:
                        partly_similar_independent_versions.add(ver1)
                        partly_similar_independent_versions.add(ver2)

        correct_partly_similar_versions = {
            ver
            for ver in partly_similar_versions
            if random() <= ver.reliability
        }
        error_partly_similar_versions = (
            partly_similar_versions - correct_partly_similar_versions
        )
        error_partly_abs_depended_versions = (
            error_partly_similar_versions & partly_similar_depended_versions
        )
        error_partly_abs_independent_versions = (
            error_partly_similar_versions & partly_similar_independent_versions
        )
        error_partly_similar_versions -= (
            error_partly_abs_depended_versions
            | error_partly_abs_independent_versions
        )

        partly_similar_base_error_val = round(
            uniform(self.module.min_out_val, self.module.max_out_val),
            self.module.round_to,
        )

        for ver in correct_partly_similar_versions:
            result_lst.append(
                self.create_result(
                    ver,
                    cur_correct_val,
                    cur_correct_val,
                    i,
                    experiment_name,
                )
            )

        for ver in error_partly_abs_depended_versions:
            result_lst.append(
                self.create_result(
                    ver,
                    partly_similar_base_error_val,
                    cur_correct_val,
                    i,
                    experiment_name,
                )
            )

        for ver in error_partly_similar_versions:
            partly_similar_error_val = self.generate_error_value(
                partly_similar_base_error_val, cur_partly_similar_diversity
            )
            result_lst.append(
                self.create_result(
                    ver,
                    partly_similar_error_val,
                    cur_correct_val,
                    i,
                    experiment_name,
                )
            )

        for ver in error_partly_abs_independent_versions:
            partly_similar_independent_error_val = round(
                uniform(self.module.min_out_val, self.module.max_out_val),
                self.module.round_to,
            )
            result_lst.append(
                self.create_result(
                    ver,
                    partly_similar_independent_error_val,
                    cur_correct_val,
                    i,
                    experiment_name,
                )
            )

    def process_difference_versions(
        self,
        difference_versions,
        cur_correct_val,
        result_lst,
        i,
        experiment_name,
    ):
        for ver in difference_versions:
            cur_difference_reliability = random()
            cur_dif_version_answer = (
                cur_correct_val
                if cur_difference_reliability <= ver.reliability
                else round(
                    uniform(self.module.min_out_val, self.module.max_out_val),
                    self.module.round_to,
                )
            )
            result_lst.append(
                self.create_result(
                    ver,
                    cur_dif_version_answer,
                    cur_correct_val,
                    i,
                    experiment_name,
                )
            )

    def generate_experiment_data(
        self, iterations_amount: int, experiment_name: str
    ) -> list:
        # Чтобы не возникало неопределённости при записи результатов в БД, очищаем имеющиеся результаты перед генерацией
        self.module._global_results_lst_2_write = list()
        self.module._global_results_lst = list()
        # Запускаем цикл по количеству заданных итераций
        for i in range(iterations_amount):
            result_lst = list()
            # Разбиваем версии на группы для различной генерации результатов их работы
            (
                clone_versions,
                similar_versions,
                partly_similar_versions,
                difference_versions,
            ) = self.group_versions()
            # Генерируем значение, которое будет считаться правильным ответом на текущей итерации
            cur_correct_val = round(
                uniform(self.module.min_out_val, self.module.max_out_val),
                self.module.round_to,
            )
            # ---------------------------------------------------------------
            # 1. Генерируем выходные данные для версий-клонов
            self.process_clone_versions(
                clone_versions,
                cur_correct_val,
                result_lst,
                i,
                experiment_name,
            )
            # 2. Генерируем выходные данные для явно схожих версий
            self.process_similar_versions(
                similar_versions,
                cur_correct_val,
                result_lst,
                i,
                experiment_name,
            )
            # 3. Генерируем выходные данные для частично схожих версий
            self.process_partly_similar_versions(
                partly_similar_versions,
                cur_correct_val,
                result_lst,
                i,
                experiment_name,
            )
            # 4. Генерируем выходные данные для явно несхожих версий
            self.process_difference_versions(
                difference_versions,
                cur_correct_val,
                result_lst,
                i,
                experiment_name,
            )
            # ---------------------------------------------------------------
            self.module._global_results_lst.append(result_lst)
        self.module._experiment_name = experiment_name
        self.module._get_global_results_lst_2_write()
        return self.module.global_results_lst
