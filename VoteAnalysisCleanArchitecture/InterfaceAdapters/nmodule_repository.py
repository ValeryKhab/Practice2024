import json

from VoteAnalysisCleanArchitecture.Entities.n_result import NResult
from VoteAnalysisCleanArchitecture.Entities.n_module import NModule, input_num
from VoteAnalysisCleanArchitecture.Entities.n_version import NVersion
from InterfaceAdapters.data_base_connector import DBConnector
from InterfaceAdapters.nversion_repository import NVersionRepository


class NModuleRepository:
    def __init__(self, module: NModule):
        self.dbConnector = DBConnector('experiment.db')
        self.module = module

    def get_version_by_id(self, id_4_search: int) -> NVersion | None:
        for cur_ver in self.module.versions_list:
            if cur_ver.id is not None and cur_ver.id == id_4_search:
                return cur_ver
        else:
            return None

    def save_module(self):
        if not self.dbConnector.table_exists('module'):
            create_query = '''
                create table module (
                    "id" integer primary key autoincrement not null,
                    "name" varchar(255) not null, "round_to" integer not null, 
                    "dynamic_diversities_intervals" varchar(1024) null, 
                    "const_diversities_count" integer not null, 
                    "dynamic_diversities_count" integer null, 
                    "min_out_val" real not null, "max_out_val" real null
                );
            '''
            self.dbConnector.execute_query(create_query, [], True, False)

        if self.module.id is None:
            insert_query = f'''
                insert into module (name, round_to, dynamic_diversities_intervals, const_diversities_count, 
                dynamic_diversities_count, min_out_val, max_out_val) values (
                    '{self.module.name}', {self.module.round_to}, 
                    '{json.dumps(self.module.dynamic_diversities_intervals_dict)}', 
                    {self.module.const_diversities_count}, {self.module.dynamic_diversities_count}, 
                    {self.module.min_out_val}, {self.module.max_out_val}
                );
            '''
            # Т.к. у нас возвращается список кортежей, берём первый элемент первого кортежа, т.к. id сего 1 возвращется!
            self.module._id = self.dbConnector.execute_query(insert_query, [], True)[0][0]
        else:
            update_query = f'''
                update module set name = '{self.module.name}', round_to = {self.module.round_to}, 
                dynamic_diversities_intervals = '{json.dumps(self.module.dynamic_diversities_intervals_dict)}', 
                const_diversities_count = '{self.module.const_diversities_count}', 
                dynamic_diversities_count = {self.module.dynamic_diversities_count}, 
                min_out_val = {self.module.min_out_val}, max_out_val = {self.module.max_out_val} where id = {self.module._id};
            '''
            self.dbConnector.execute_query(update_query, [], True, False)

    def save_module_with_versions(self):
        self.save_module()
        for ver in self.module.versions_list:
            version_rep = NVersionRepository(ver)
            version_rep.save(self.module.id)

    def save_experiment_data(self):
        if not self.module.global_results_lst_2_write or len(self.module.global_results_lst_2_write) == 0:
            raise LookupError('There is no experiment data to save into data base')

        if not self.dbConnector.table_exists('experiment_data'):
            create_query = '''
                create table experiment_data (
                    "id" integer primary key autoincrement not null, 
                    version_id integer not null, version_name varchar(255), 
                    version_reliability real not null, 
                    version_common_coordinates varchar(1024) not null, 
                    version_answer real not null, 
                    correct_answer real not null, 
                    module_id integer not null, module_name varchar(255), 
                    module_connectivity_matrix varchar(4095), 
                    module_iteration_num int not null, 
                    experiment_name varchar(31) not null, 
                    unique(version_id, version_reliability, version_common_coordinates, 
                    version_answer, correct_answer, module_id, module_connectivity_matrix, 
                    module_iteration_num) on conflict replace, 
                    foreign key ("version_id") references version(id), 
                    foreign key ("module_id") references module(id)
                );
            '''
            self.dbConnector.execute_query(create_query, [], True, False)
        # Обращаемся к первому результату первой итерации для провеки, присвоен ли ему id, чтобы понять, надо ли
        # сохранять результаты, или они уже сохранены, т.к. можно только перегенерировать их, но не изменить
        if self.module._global_results_lst[0][0].id is None:
            insert_query = '''
                insert into experiment_data (version_id, version_name, version_reliability, 
                version_common_coordinates, version_answer, correct_answer, module_id, module_name, 
                module_connectivity_matrix, module_iteration_num, experiment_name) values (
                    ?,?,?,?,?,?,?,?,?,?,?
                );
            '''
            self.dbConnector.execute_query(insert_query, self.module.global_results_lst_2_write, True, False)

            if input('Do you want to load IDs of saved data? Yes - Y; No - any key').upper() == 'Y':
                self.load_experiment_data(self.module._experiment_name)

    def load_experiment_data(self, experiment_name: str = None):
        if not self.dbConnector.table_exists('experiment_data'):
            raise LookupError(
                f'There is no "EXPERIMENT_DATA" table in {self.dbConnector.db_name} data base. Save experiment data before load it'
            )
        can_we_go_further = False
        if experiment_name is None and self.module._experiment_name is not None:
            experiment_name = self.module._experiment_name
            can_we_go_further = True

        if experiment_name is not None:
            can_we_go_further = True

        if can_we_go_further:
            select_query = f'''
                select id, version_id, version_name, version_reliability, version_common_coordinates, 
                version_answer, correct_answer, module_id, module_name, module_connectivity_matrix, 
                module_iteration_num, experiment_name from experiment_data where experiment_name = '{experiment_name}';
            '''
            select_res = self.dbConnector.execute_query(select_query)
            # Если удалось загрузить данные из БД,
            if len(select_res) > 0:
                # то очищает имеющиеся списки с результатами для загрузки новых данных
                self.module._global_results_lst = list()
                self.module._global_results_lst_2_write = list()

            cur_iter_num = None
            cur_iter_list = []
            for res in select_res:
                # Если это не самая первая итерация и итерация эксперимента сменилась, записываем собранные данные в
                # глобальный список и очищаем временный список
                if cur_iter_num is not None and cur_iter_num != res[10]:
                    self.module._global_results_lst.append(cur_iter_list)
                    cur_iter_list = list()

                cur_iter_num = res[10]
                cur_iter_list.append(NResult(res[1], res[2], res[3], json.loads(res[4])['version_coordinates'],
                                             res[5], res[6], res[7], res[8],
                                             json.loads(res[9])['connectivity_matrix'], res[10],
                                             self.get_version_by_id(res[1]), res[0], res[11]))
                if self.module._experiment_name is None:
                    self.module._experiment_name = res[11]

            if len(select_res) > 0:
                # Дозаписываем данные в глобальный массив результатов с последней итерации эксперимента
                self.module._global_results_lst.append(cur_iter_list)

            self.module._get_global_results_lst_2_write()
        else:
            raise ValueError(
                f'Unexpected value {experiment_name} of experiment_name parameter!'
            )

    def get_experiments_names(self):
        if self.dbConnector.table_exists('experiment_data'):
            experiment_select_res = self.dbConnector.execute_query("select distinct experiment_name from experiment_data;")
            return [exp_name[0] for exp_name in experiment_select_res]

    def load_module(self):
        if not self.dbConnector.table_exists('module'):
            raise LookupError(
                f'There is no "MODULE" table in {self.dbConnector.db_name} data base. Save module data before load it.'
            )
        if self.module.id is None:
            q_set = self.dbConnector.execute_query('select distinct id, name, round_to from module order by id;')
            get_num_str = 'Choice module by id to load it.\n'
            for mdl in q_set:
                get_num_str += f'\n{str(mdl)}'
            get_num_str += '\n'
            chosen_id = input_num(get_num_str)
        else:
            chosen_id = self.module.id

        select_query = f'''
            select id, name, round_to, dynamic_diversities_intervals, 
            const_diversities_count, dynamic_diversities_count, 
            min_out_val, max_out_val from module where id = {chosen_id};
        '''
        select_res = self.dbConnector.execute_query(select_query)

        # Т.к. у нас только 1 модуль может быть найден по id, то обращаемся мы к 0-му индексу, без доп. проверок
        self.module._id = select_res[0][0]
        self.module.name = select_res[0][1]
        self.module.round_to = select_res[0][2]
        self.module._dynamic_diversities_intervals_dict = json.loads(select_res[0][3])
        self.module._const_diversities_count = select_res[0][4]
        self.module._dynamic_diversities_count = select_res[0][5]
        self.module.min_out_val = select_res[0][6]
        self.module.max_out_val = select_res[0][7]
        return self.module

    def load_module_with_versions(self):
        try:
            self.load_module()
            version_rep = NVersionRepository(None)
            self.module._versions_list = version_rep.load_versions_2_module(self.module.id)
            return self.module
        except (LookupError, AttributeError) as e:
            print(str(e))
