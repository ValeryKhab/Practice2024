import inspect
import json
import os

from InterfaceAdapters.data_base_connector import DBConnector
from VoteAnalysisCleanArchitecture.UseCases.vote_algorithm import \
    VoteAlgorithm, ModuleNotLoadedError, FunctionNotFoundInModuleError


class VoteAlgorithmRepository:
    def __init__(self, vote_algorithm: VoteAlgorithm):
        self.dbConnector = DBConnector('experiment.db')
        self.voteAlgorithm = vote_algorithm

    def save_vote_algorithm(self):
        if not self.dbConnector.table_exists('algorithm'):
            create_query = '''
                create table algorithm (
                    id integer primary key autoincrement not null,
                    name varchar(127) not null,
                    src_code text null,
                    module_name varchar(255) not null,
                    func_name varchar(127) not null,
                    module_pkg varchar(255) null
                );
            '''
            self.dbConnector.execute_query(create_query, [], True, False)

        if self.voteAlgorithm._id is None:
            insert_query = f'''
                insert into algorithm (name, src_code, module_name, func_name, module_pkg) values (
                    '{str(self.voteAlgorithm.name)}', '{json.dumps(inspect.getsource(self.voteAlgorithm._vote_module))}',
                    '{self.voteAlgorithm.module_name}', '{self.voteAlgorithm._vote_func_name}', 'VoteAlgorithms'
                );
            '''
            # Возвращается список кортежей, берём первый элемент первого кортежа, т.к. id всего 1 возвращется!
            self.voteAlgorithm._id = self.dbConnector.execute_query(insert_query, [], True)[0][0]
        else:
            update_query = f'''
                update algorithm set name = '{self.voteAlgorithm.name}',
                src_code = '{json.dumps(inspect.getsource(self.voteAlgorithm._vote_algorithm))}',
                module_path = '{self.voteAlgorithm.module_name}' where id = {self.voteAlgorithm._id};
            '''
            self.dbConnector.execute_query(update_query, [], True, False)

    def save_vote_results(self):
        if not self.dbConnector.table_exists('vote_result'):
            create_query = '''
                create table vote_result (
                    id integer primary key autoincrement not null,
                    algorithm_id integer not null,
                    experiment_data_id integer not null,
                    vote_answer real null,
                    unique(algorithm_id, experiment_data_id, vote_answer) on conflict replace,
                    foreign key ("algorithm_id") references algorithm(id),
                    foreign key ("experiment_data_id") references experiment_data(id)
                );
            '''
            self.dbConnector.execute_query(create_query, [], True, False)

        if self.voteAlgorithm._id is None:
            self.save_vote_algorithm()

        res_insert_lst = list()
        for res in self.voteAlgorithm._vote_result:
            for iteration_res in res['data']:
                res_insert_lst.append((self.voteAlgorithm._id, iteration_res.id, res['res']))
        if len(res_insert_lst) > 0:
            insert_query = 'insert into vote_result (algorithm_id, experiment_data_id, vote_answer) values(?,?,?);'
            self.dbConnector.execute_query(insert_query, res_insert_lst, True, False)

            if input(
                    'Do you want to load rows is from DB? y - Yes; any key - No: ').upper() == 'Y':
                for res in self.voteAlgorithm._vote_result:
                    tmp_ids: list[int] = list()
                    for iteration_res in res['data']:
                        select_query = f'''
                            select id from vote_result where algorithm_id = {self.voteAlgorithm._id}
                            and experiment_data_id = {iteration_res.id} 
                            and vote_answer = {res['res']};
                        '''
                        select_res = self.dbConnector.execute_query(select_query)
                        if len(select_res) > 0 and len(select_res[0]) > 0:
                            tmp_ids.append(int(select_res[0][0]))
                    res['ids'] = tmp_ids

    def load_vote_results(self):
        # TODO: Дописать этот метод!
        pass

    def load_algorithms(self) -> list:
        algorithms_list = list()
        if not self.dbConnector.table_exists('algorithm'):
            raise LookupError(
                f'There is no "algorithm" table in {self.dbConnector.db_name} data base. Save some algorithm before load it.')
        select_query = 'select id, name, func_name, module_name, src_code, module_pkg from algorithm order by id;'
        q_set = self.dbConnector.execute_query(select_query)
        common_err_msg = 'Row is skipped'
        for mdl in q_set:
            try:
                m_id = int(mdl[0])
            except ValueError:
                print(
                    f'Incorrect algorithm identifier - {mdl[0]}. {common_err_msg}')
                continue
            else:
                m_alg_name, m_func, m_name, m_code, m_pkg = mdl[1], mdl[2], \
                mdl[3], mdl[4], mdl[5]
                # Если путь валидный, то присваиваем его переменной для инициализации нового алгоритма
                if not os.path.isfile(f'{m_pkg}/{m_name}.py'):
                    # Иначе создаём файл с исходным кодом из БД по этому пути
                    with open(f'{m_pkg}/{m_name}.py', 'w') as mod_file:
                        mod_file.write(json.loads(m_code))
                try:
                    algorithms_list.append(
                        VoteAlgorithm(m_alg_name, m_func, m_name, m_pkg, m_id))
                except (ModuleNotFoundError, ModuleNotLoadedError,
                        FunctionNotFoundInModuleError) as e:
                    print(f'Error: {e.msg}. {common_err_msg}')
                except Exception as e:
                    print(f'Error: {e}. {common_err_msg}')
        return algorithms_list
