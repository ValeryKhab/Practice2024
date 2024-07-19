from VoteAnalysisCleanArchitecture.Entities.n_result import NResult
from VoteAnalysisCleanArchitecture.Entities.vote_algorithm import VoteAlgorithm


class VoteAlgorithmRunner:
    def __init__(self, vote_algorithm: VoteAlgorithm):
        self.vote_algorithm = vote_algorithm

    def vote(self, nversions_results: list[list[NResult]]):
        self.vote_algorithm._vote_result = list()
        for iteration_result in nversions_results:
            self.vote_algorithm._vote_result.append(
                {
                    "data": iteration_result,
                    "res": self.vote_algorithm._vote_algorithm(
                        iteration_result
                    ),
                }
            )
        return self.vote_algorithm._vote_result
