from VoteAnalysisCleanArchitecture.Entities.n_result import NResult
import random


error_string = "Input list is empty"


def classic_vote(results: list[NResult], return_classes_list: bool = False) -> float:
    if not results or len(results) == 0:
        print(error_string)
        raise ValueError(error_string)

    classes_list: list[list] = []
    for res in results:
        # Если другие мультиверсии уже выставили свои ответы на голосование, то сравниваем текущий ответ с ними
        # Если обрабатываемый ответ относится к уже имеющемуся классу, то добавляем его в этот класс.
        for answers_class in classes_list:
            if res.version_answer == answers_class[0].version_answer:
                answers_class.append(res)
                break
        else:  # Иначе создаём новый класс для ответа, т.к. он встретился впервые
            classes_list.append([res])

    if not classes_list or len(classes_list) == 0:
        print(error_string)
        raise ValueError(error_string)

    # Если есть из чего выбирать, выбираем первую группу, которая имеет наибольшее число одинаковых ответов
    if return_classes_list:
        return classes_list

    max_classes = [classes_list[0]]
    max_values_in_class = len(classes_list[0])
    for answers_class in classes_list:
        if len(answers_class) > max_values_in_class:
            max_values_in_class = len(answers_class)
            max_classes = [answers_class]
        elif len(answers_class) == max_values_in_class != 0:
            max_classes.append(answers_class)

    # Если есть 2 или более класса с одинаковым количеством ответов, то выбираем из них случайным образом
    if len(max_classes) > 1:
        max_class = random.choice(max_classes)
    else:
        max_class = max_classes[0]
    # Т.к. во вложенном списке хранятся одинаковые результаты, мы можем возвращать любой, например 0-й
    return max_class[0].version_answer


def calc_versions_diversity(results_list: list[NResult]) -> float:
    if not results_list or len(results_list) == 0:
        print(error_string)
        raise ValueError(error_string)
    if len(results_list) == 1:
        # Если в списке всего одно значение, то формально - это множество из 1-го элемента, он сам от себя не
        # отличается, поэтому можно было бы считать данную группу недеверсифицированной,
        return 0
    max_diversity: float = 0
    for j in range(len(results_list)):
        for k in range(j + 1, len(results_list)):
            cur_diversity = results_list[j].version.calculate_distance_to(results_list[k].version)
            max_diversity = max(max_diversity, cur_diversity)
    return max_diversity


def modified_vote(results: list[NResult]) -> float:
    try:
        classes_list = classic_vote(results, True)
    except ValueError as err:
        print(str(err))
        raise ValueError(str(err))

    max_classes = [classes_list[0]]
    max_values_in_class = len(classes_list[0])
    max_length = calc_versions_diversity(classes_list[0])
    for i in range(len(classes_list)):
        class_len = len(classes_list[i])
        if 0 < class_len:
            tmp_max_len = calc_versions_diversity(classes_list[i])
            # Если в одной группе ответов больше чем в другой, однозначно определяем группу (класс) с верным ответом
            # Если 2 класса содержат одинаковое число ответов,
            # то пробуем посмотреть на уровень диверсифицированности этих групп - выбираем ту, где версии более
            # различны между собой
            if class_len > max_values_in_class or (class_len == max_values_in_class and tmp_max_len > max_length):
                max_values_in_class = class_len
                max_classes = [classes_list[i]]
                max_length = tmp_max_len
            elif class_len == max_length and tmp_max_len == max_length: # Если и число версий в классе, и диверсифицированность версий
                # внутри классов одинаковые, то возвращаемся к классическому методу - выбираем случайно, т.к.
                # нет дополнительной информации
                max_classes.append(classes_list[i])

    # Если есть 2 или более класса с одинаковым количеством ответов и одинаковым уровнем диверсифицированности, то
    # выбираем из них случайным образом
    if len(max_classes) > 1:
        max_class = random.choice(max_classes)
    else:
        max_class = max_classes[0]
    # Т.к. во вложенном списке хранятся одинаковые результаты, мы можем возвращать любой, например 0-й
    return max_class[0].version_answer
