from statistics import median
from VoteAnalysisCleanArchitecture.Entities.n_result import NResult


def vote(results: list[NResult]) -> float:
    res_lst = [res.version_answer for res in results]
    return median(res_lst)
