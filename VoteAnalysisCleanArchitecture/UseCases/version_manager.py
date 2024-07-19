from VoteAnalysisCleanArchitecture.Entities.n_module import NModule, input_num
from VoteAnalysisCleanArchitecture.Entities.n_version import NVersion


class VersionManager:
    def __init__(self, module: NModule):
        self.module = module

    def add_versions(self):
        while (
            input(
                "Add new version to module? Yes - any key; No - n. Your choice: "
            )
            != "n"
        ):
            cur_new_version = NVersion()
            cur_new_version.name = input("Enter version name: ")

            if self.module._const_diversities_count < 1:
                self.module._const_diversities_count = input_num(
                    "Enter constant diversity metrics count: ",
                    (0, float("inf")),
                )
            if self.module._dynamic_diversities_count < 1:
                self.module._dynamic_diversities_count = input_num(
                    "Enter dynamic diversity metrics count: ",
                    (0, float("inf")),
                )

            const_diversities_lst = []
            for i in range(self.module._const_diversities_count):
                const_diversities_lst.append(
                    input_num(
                        f"Enter {i + 1} diversity coordinate: ",
                        (float("-inf"), float("inf")),
                        float,
                        self.module.round_to,
                    )
                )
            cur_new_version.const_diversities = tuple(const_diversities_lst)
            self.module._const_diversities_versions_list.append(
                cur_new_version.const_diversities
            )

            tmp_dynamic_diversities_lst = []
            for i in range(self.module._dynamic_diversities_count):
                print(
                    f"Enter limits (from min to max) to generate {i + 1} diversity coordinate"
                )
                tmp_dynamic_diversities_lst.append(
                    (
                        input_num(
                            "Min value: ",
                            (float("-inf"), float("inf")),
                            float,
                            self.module.round_to,
                        ),
                        input_num(
                            "Max value: ",
                            (float("-inf"), float("inf")),
                            float,
                            self.module.round_to,
                        ),
                    )
                )
            self.module._dynamic_diversities_intervals_dict[
                cur_new_version.name
            ] = tmp_dynamic_diversities_lst

            cur_new_version.reliability = input_num(
                "Reliability: ", (0, 1), float, True, self.module.round_to
            )
            cur_new_version.generate_dynamic_diversities(
                self.module._dynamic_diversities_intervals_dict[
                    cur_new_version.name
                ],
                self.module.round_to,
            )
            self.module._versions_list.append(cur_new_version)
        return self.module.versions_list
