import os


class ModuleNotLoadedError(Exception):
    pass


class FunctionNotFoundInModuleError(Exception):
    pass


class VoteAlgorithm:
    def __init__(
        self,
        name: str,
        vote_func_name: str,
        module_name: str,
        module_pkg: str = "VoteAlgorithms",
        new_id=None,
    ):
        self.name = name
        self._module_name = module_name
        self._vote_func_name = vote_func_name
        self._id = new_id
        self._vote_module = None
        self._vote_algorithm = None
        self._vote_result: list[dict] = []

        try:
            self._module_pkg = __import__(f"{module_pkg}.{module_name}")
            if not hasattr(self._module_pkg, module_name):
                raise ModuleNotLoadedError(
                    f"Cannot load module {module_pkg}.{module_name}"
                )
            self._vote_module = getattr(self._module_pkg, module_name)
            if not hasattr(self._vote_module, vote_func_name):
                raise FunctionNotFoundInModuleError(
                    f"There is no function {vote_func_name} in {module_name}"
                )
            self._vote_algorithm = getattr(self._vote_module, vote_func_name)
        except ModuleNotFoundError as e:
            raise e
        except Exception as e:
            print(e.__str__())
            raise e

    @property
    def vote_algorithm(self):
        return self._vote_algorithm

    @vote_algorithm.setter
    def vote_algorithm(self, vote_func):
        self._vote_algorithm = vote_func

    @property
    def vote_results(self):
        return self._vote_result

    @property
    def module_name(self):
        return self._module_name

    @module_name.setter
    def module_name(self, new_path: str):
        if os.path.isfile(new_path):
            self._module_name = new_path
        else:
            raise ModuleNotFoundError(
                f"Cannot find module by path: {new_path}"
            )

    def __str__(self):
        return f"{self.name} ({self._vote_func_name}) in {self._module_name}"
