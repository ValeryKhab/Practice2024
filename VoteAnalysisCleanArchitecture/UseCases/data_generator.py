from random import random, normalvariate, uniform
from VoteAnalysisCleanArchitecture.Entities.n_result import NResult


def group_versions(module):
    clone_versions = set()
    similar_versions = set()
    partly_similar_versions = set()
    difference_versions = set()
    for j in range(len(module.versions_list)):
        for k in range(len(module.versions_list)):
            if k > j:
                if 0 <= module.normed_connectivity_matrix[j][k] <= 0.05:
                    add_to_set(module, clone_versions, j, k)
                elif 0.05 < module.normed_connectivity_matrix[j][k] < 0.4:
                    add_to_set(module, similar_versions, j, k)
                elif 0.4 <= module.normed_connectivity_matrix[j][k] <= 0.6:
                    add_to_set(module, partly_similar_versions, j, k)
                else:
                    add_to_set(module, difference_versions, j, k)
    return clone_versions, similar_versions, partly_similar_versions, difference_versions


def add_to_set(module, version_set, j, k):
    if module.versions_list[j] not in version_set:
        version_set.add(module.versions_list[j])
    if module.versions_list[k] not in version_set:
        version_set.add(module.versions_list[k])


def create_result(module, ver, v_answer, cur_correct_val, i, experiment_name):
    return NResult(
        v_id=ver.id,
        v_name=ver.name,
        v_reliability=ver.reliability,
        v_common_coordinates=ver.common_coordinates_list,
        v_answer=v_answer,
        c_answer=cur_correct_val,
        m_id=module.id,
        m_name=module.name,
        m_connectivity_matrix=module.normed_connectivity_matrix,
        m_iteration_num=i,
        version=ver,
        experiment_name=experiment_name
    )


def generate_error_value(module, base_val, diversity_coefficient):
    return round(normalvariate(base_val, diversity_coefficient * base_val),
                 module.round_to)


def process_clone_versions(module, clone_versions, cur_correct_val,
                           result_lst, i, experiment_name):
    min_rel = min(ver.reliability for ver in clone_versions)

    cur_clone_reliability = random()

    for ver in clone_versions:
        if cur_clone_reliability <= min_rel:
            result_lst.append(
                create_result(module, ver, cur_correct_val, cur_correct_val,
                              i, experiment_name))
        else:
            clone_error_val = round(
                uniform(module.min_out_val, module.max_out_val),
                module.round_to)
            result_lst.append(
                create_result(module, ver, clone_error_val, cur_correct_val,
                              i, experiment_name))


def process_similar_versions(module, similar_versions, cur_correct_val,
                             result_lst, i, experiment_name):
    cur_similar_reliability = random()
    correct_similar_versions = {ver for ver in similar_versions if
                                cur_similar_reliability <= ver.reliability}
    similar_base_error_val = cur_correct_val if correct_similar_versions else round(
        uniform(module.min_out_val, module.max_out_val), module.round_to)
    diversity_coefficient = round(uniform(0.06, 0.39), module.round_to)

    for ver in similar_versions:
        if cur_similar_reliability > ver.reliability:
            similar_error_val = generate_error_value(
                module, similar_base_error_val, diversity_coefficient)
            result_lst.append(
                create_result(module, ver, similar_error_val, cur_correct_val,
                              i, experiment_name))
        else:
            result_lst.append(
                create_result(module, ver, cur_correct_val, cur_correct_val,
                              i, experiment_name))


def process_partly_similar_versions(module, partly_similar_versions,
                                    cur_correct_val, result_lst, i,
                                    experiment_name):
    cur_partly_similar_diversity = random()
    partly_similar_depended_versions = set()
    partly_similar_independent_versions = set()

    for ver1 in partly_similar_versions:
        for ver2 in partly_similar_versions:
            if ver1 != ver2:
                v1_index = module.versions_list.index(ver1)
                v2_index = module.versions_list.index(ver2)
                if module.normed_connectivity_matrix[v1_index][v2_index] >= cur_partly_similar_diversity:
                    partly_similar_depended_versions.add(ver1)
                    partly_similar_depended_versions.add(ver2)
                else:
                    partly_similar_independent_versions.add(ver1)
                    partly_similar_independent_versions.add(ver2)

    correct_partly_similar_versions = {ver for ver in partly_similar_versions
                                       if random() <= ver.reliability}
    error_partly_similar_versions = partly_similar_versions - correct_partly_similar_versions
    error_partly_abs_depended_versions = error_partly_similar_versions & partly_similar_depended_versions
    error_partly_abs_independent_versions = error_partly_similar_versions & partly_similar_independent_versions
    error_partly_similar_versions -= (
            error_partly_abs_depended_versions | error_partly_abs_independent_versions)

    partly_similar_base_error_val = round(
        uniform(module.min_out_val, module.max_out_val), module.round_to)

    for ver in correct_partly_similar_versions:
        result_lst.append(
            create_result(module, ver, cur_correct_val, cur_correct_val,
                          i, experiment_name))

    for ver in error_partly_abs_depended_versions:
        result_lst.append(
            create_result(module, ver, partly_similar_base_error_val,
                          cur_correct_val, i, experiment_name))

    for ver in error_partly_similar_versions:
        partly_similar_error_val = generate_error_value(
            module, partly_similar_base_error_val,
            cur_partly_similar_diversity)
        result_lst.append(
            create_result(module, ver, partly_similar_error_val,
                          cur_correct_val, i, experiment_name))

    for ver in error_partly_abs_independent_versions:
        partly_similar_independent_error_val = round(
            uniform(module.min_out_val, module.max_out_val), module.round_to)
        result_lst.append(
            create_result(module, ver, partly_similar_independent_error_val,
                          cur_correct_val, i, experiment_name))


def process_difference_versions(module, difference_versions, cur_correct_val,
                                result_lst, i, experiment_name):
    for ver in difference_versions:
        cur_difference_reliability = random()
        cur_dif_version_answer = cur_correct_val if cur_difference_reliability <= ver.reliability else round(
            uniform(module.min_out_val, module.max_out_val), module.round_to)
        result_lst.append(
            create_result(module, ver, cur_dif_version_answer, cur_correct_val,
                          i, experiment_name))


def generate_experiment_data(module, iterations_amount: int,
                             experiment_name: str) -> list:
    # Чтобы не возникало неопределённости при записи результатов в БД, очищаем имеющиеся результаты перед генерацией
    module._global_results_lst_2_write = list()
    module._global_results_lst = list()
    # Запускаем цикл по количеству заданных итераций
    for i in range(iterations_amount):
        result_lst = list()
        # Разбиваем версии на группы для различной генерации результатов их работы
        clone_versions, similar_versions, partly_similar_versions, difference_versions = group_versions(
            module)
        # Генерируем значение, которое будет считаться правильным ответом на текущей итерации
        cur_correct_val = uniform(module.min_out_val,
                                  module.max_out_val).__round__(
            module.round_to)
        # ---------------------------------------------------------------
        # 1. Генерируем выходные данные для версий-клонов
        process_clone_versions(module, clone_versions, cur_correct_val,
                               result_lst, i, experiment_name)
        # 2. Генерируем выходные данные для явно схожих версий
        process_similar_versions(module, similar_versions, cur_correct_val,
                                 result_lst, i, experiment_name)
        # 3. Генерируем выходные данные для частично схожих версий
        process_partly_similar_versions(module, partly_similar_versions,
                                        cur_correct_val, result_lst,
                                        i, experiment_name)
        # 4. Генерируем выходные данные для явно несхожих версий
        process_difference_versions(module, difference_versions,
                                    cur_correct_val, result_lst, i,
                                    experiment_name)
        # ---------------------------------------------------------------
        module._global_results_lst.append(result_lst)
    module._experiment_name = experiment_name
    module._get_global_results_lst_2_write()
    return module.global_results_lst
