"""Vote algorithm model to make a vote and save and load it

Program for simulation several N-versions work of one module to test vote algorithms.
Experiment is carried out in Denis V. Gruzenkin PhD thesis writing.
"""
import inspect
import json
import os

from data_base_connector import DBConnector
from data_generator import NResult
from module_importer import ModuleNotLoadedError, FunctionNotFoundInModuleError

__author__ = "Denis V. Gruzenkin"
__copyright__ = "Copyright 2021, Denis V. Gruzenkin"
__credits__ = ["Denis V. Gruzenkin"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Denis V. Gruzenkin"
__email__ = "gruzenkin.denis@good-look.su"
__status__ = "Production"


class VoteAlgorithm:
    _db_name = "experiment.db"

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
                    f"Cannot load module VoteAlgorithms.{module_name}"
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

    def vote(self, nversions_results: list[list[NResult]]):
        self._vote_result = list()
        for iteration_result in nversions_results:
            self._vote_result.append(
                {
                    "data": iteration_result,
                    "res": self._vote_algorithm(iteration_result),
                }
            )

    def save_vote_algorithm(self):
        cur_conn = DBConnector(self._db_name)
        if not cur_conn.table_exists("algorithm"):
            create_query = """
                create table algorithm (
                    id integer primary key autoincrement not null,
                    name varchar(127) not null,
                    src_code text null,
                    module_name varchar(255) not null,
                    func_name varchar(127) not null,
                    module_pkg varchar(255) null
                );
            """
            cur_conn.execute_query(create_query, [], True, False)

        if self._id is None:
            insert_query = f"""
                insert into algorithm (name, src_code, module_name, func_name, module_pkg) values (
                    '{str(self.name)}', '{json.dumps(inspect.getsource(self._vote_module))}',
                    '{self._module_name}', '{self._vote_func_name}', 'VoteAlgorithms'
                );
            """
            # Возвращается список кортежей, берём первый элемент первого кортежа, т.к. id всего 1 возвращется!
            self._id = cur_conn.execute_query(insert_query, [], True)[0][0]
        else:
            update_query = f"""
                update algorithm set name = '{self.name}',
                src_code = '{json.dumps(inspect.getsource(self._vote_algorithm))}',
                module_path = '{self._module_name}' where id = {self._id};
            """
            cur_conn.execute_query(update_query, [], True, False)

    def save_vote_results(self):
        cur_conn = DBConnector(self._db_name)
        if not cur_conn.table_exists("vote_result"):
            create_query = """
                create table vote_result (
                    id integer primary key autoincrement not null,
                    algorithm_id integer not null,
                    experiment_data_id integer not null,
                    vote_answer real null,
                    unique(algorithm_id, experiment_data_id, vote_answer) on conflict replace,
                    foreign key ("algorithm_id") references algorithm(id),
                    foreign key ("experiment_data_id") references experiment_data(id)
                );
            """
            cur_conn.execute_query(create_query, [], True, False)

        if self._id is None:
            self.save_vote_algorithm()

        res_insert_lst = list()
        for res in self._vote_result:
            for iteration_res in res["data"]:
                res_insert_lst.append((self._id, iteration_res.id, res["res"]))
        if len(res_insert_lst) > 0:
            insert_query = "insert into vote_result (algorithm_id, experiment_data_id, vote_answer) values(?,?,?);"
            cur_conn.execute_query(insert_query, res_insert_lst, True, False)

            if (
                input(
                    "Do you want to load rows is from DB? y - Yes; any key - No: "
                ).upper()
                == "Y"
            ):
                for res in self._vote_result:
                    tmp_ids: list[int] = list()
                    for iteration_res in res["data"]:
                        select_query = f"""
                            select id from vote_result where algorithm_id = {self._id}
                            and experiment_data_id = {iteration_res.id} 
                            and vote_answer = {res['res']};
                        """
                        select_res = cur_conn.execute_query(select_query)
                        if len(select_res) > 0 and len(select_res[0]) > 0:
                            tmp_ids.append(int(select_res[0][0]))
                    res["ids"] = tmp_ids

    def load_vote_results(self):
        # TODO: Дописать этот метод!
        pass

    @classmethod
    def load_algorithms(cls) -> list:
        cur_conn = DBConnector(cls._db_name)
        algorithms_list = list()
        if not cur_conn.table_exists("algorithm"):
            raise LookupError(
                f'There is no "algorithm" table in {cls._db_name} data base. Save some algorithm before load it.'
            )
        select_query = "select id, name, func_name, module_name, src_code, module_pkg from algorithm order by id;"
        q_set = cur_conn.execute_query(select_query)
        common_err_msg = "Row is skipped"
        for mdl in q_set:
            try:
                m_id = int(mdl[0])
            except ValueError:
                print(
                    f"Incorrect algorithm identifier - {mdl[0]}. {common_err_msg}"
                )
                continue
            else:
                m_alg_name, m_func, m_name, m_code, m_pkg = (
                    mdl[1],
                    mdl[2],
                    mdl[3],
                    mdl[4],
                    mdl[5],
                )
                # Если путь валидный, то присваиваем его переменной для инициализации нового алгоритма
                if not os.path.isfile(f"{m_pkg}/{m_name}.py"):
                    # Иначе создаём файл с исходным кодом из БД по этому пути
                    with open(f"{m_pkg}/{m_name}.py", "w") as mod_file:
                        mod_file.write(json.loads(m_code))
                try:
                    algorithms_list.append(
                        VoteAlgorithm(m_alg_name, m_func, m_name, m_pkg, m_id)
                    )
                except (
                    ModuleNotFoundError,
                    ModuleNotLoadedError,
                    FunctionNotFoundInModuleError,
                ) as e:
                    print(f"Error: {e.msg}. {common_err_msg}")
                except Exception as e:
                    print(f"Error: {e}. {common_err_msg}")
        return algorithms_list

    def __str__(self):
        return f"{self.name} ({self._vote_func_name}) in {self._module_name}"
