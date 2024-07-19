from math import sqrt
from random import uniform


class NVersion:
    """
    Real NVP version emulation
    """

    def __init__(
        self,
        n_id: int = None,
        name: str = "NoName",
        const_diversities: tuple[float] = tuple(),
        dynamic_diversities: list[tuple] = None,
        reliability: float = 0,
    ):
        """
        NVersion class constructor
        :param n_id:
        :param name:
        :param const_diversities:
        :param dynamic_diversities:
        :param reliability:
        :type dynamic_diversities: list[tuple]
        """
        if dynamic_diversities is None:
            dynamic_diversities = list()
        self._id = n_id
        self._name = name
        self._const_diversities = const_diversities
        self._dynamic_diversities = dynamic_diversities
        self._reliability = reliability

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name: str):
        self._name = new_name.__str__()

    @property
    def const_diversities(self):
        return self._const_diversities

    @const_diversities.setter
    def const_diversities(self, new_tpl: tuple):
        self._const_diversities = new_tpl

    @property
    def dynamic_diversities(self):
        return self._dynamic_diversities

    @dynamic_diversities.setter
    def dynamic_diversities(self, new_lst: list):
        self._dynamic_diversities = new_lst

    @property
    def common_coordinates_list(self):
        return tuple(list(self._const_diversities) + self._dynamic_diversities)

    @property
    def reliability(self):
        return self._reliability

    @reliability.setter
    def reliability(self, new_val: float):
        if 0 <= float(new_val) <= 1:
            self._reliability = new_val
        else:
            raise ValueError("Reliability interval is [0, 1]")

    def generate_reliability(self, min_val: float, max_val: float, round_to=6):
        self._reliability = round(uniform(min_val, max_val), round_to)

    @staticmethod
    def _calc_euclidean_distance(
        lst1: list[float], lst2: list[float]
    ) -> float:
        if len(lst1) != len(lst2):
            raise ValueError("Different coordinates amount")
        return sqrt(sum((x - y) ** 2 for x, y in zip(lst1, lst2)))

    @property
    def distance_from_zero_point(self):
        return self._calc_euclidean_distance(
            self.common_coordinates_list,
            list(map(lambda arg: arg * 0, self.common_coordinates_list)),
        )

    def generate_dynamic_diversities(
        self, intervals_lst: list[tuple], round_to=6
    ):
        for tpl in intervals_lst:
            self._dynamic_diversities.append(round(uniform(*tpl), round_to))

    def calculate_distance_to(self, another_version) -> float:
        return self._calc_euclidean_distance(
            self.common_coordinates_list,
            another_version.common_coordinates_list,
        )

    def __str__(self):
        return f"{self._id}. {self._name} [{self._reliability}] {self.common_coordinates_list}"
