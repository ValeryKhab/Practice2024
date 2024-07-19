from statistics import mean
from VoteAnalysisCleanArchitecture.Entities.n_result import NResult


def vote(results: list[NResult]) -> float:
    res_lst = [res.version_answer for res in results]
    return mean(res_lst)
