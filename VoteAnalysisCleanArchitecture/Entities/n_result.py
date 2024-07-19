from Entities.n_version import NVersion


class NResult:
    def __init__(
        self,
        v_id: int,
        v_name: str,
        v_reliability: float,
        v_common_coordinates: tuple,
        v_answer: float,
        c_answer: float,
        m_id: int,
        m_name: str,
        m_connectivity_matrix: tuple,
        m_iteration_num: int,
        version: NVersion = None,
        res_id=None,
        experiment_name: str = "NoName",
    ):
        self.id = res_id
        self.version_id = v_id
        self.version_name = v_name
        self.version_reliability = v_reliability
        self.version_common_coordinates = v_common_coordinates
        self.version_answer = v_answer
        self.correct_answer = c_answer
        self.module_id = m_id
        self.module_name = m_name
        self.module_connectivity_matrix = m_connectivity_matrix
        self.module_iteration_num = m_iteration_num
        self.version = version
        self.experiment_name = experiment_name

    def __str__(self):
        result_str = f"{self.module_iteration_num}. {self.module_name} - {self.version_name} "
        result_str += f"({self.version_reliability}): Correct: {self.correct_answer}; Version answer: "
        result_str += f"{self.version_answer}"
        return result_str
