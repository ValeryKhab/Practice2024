import json

from VoteAnalysisCleanArchitecture.Entities.n_module import input_num
from VoteAnalysisCleanArchitecture.Entities.n_version import NVersion
from InterfaceAdapters.data_base_connector import DBConnector


class NVersionRepository:
    def __init__(self, version: NVersion):
        self.dbConnector = DBConnector('experiment.db')
        self.version = version
        self.formal_json_db_lst_name = list

    def save(self, module_id=None):
        if not self.dbConnector.table_exists('version'):
            create_query = '''
                create table version (
                    "id" integer primary key autoincrement not null, 
                    "name" varchar(255) not null, 
                    "const_diversities_coordinates" varchar(512) null, 
                    "dynamic_diversities_coordinates" varchar(512) null, 
                    "reliability" real not null, 
                    "module" integer null, 
                    foreign key ("module") references module(id));
            '''
            self.dbConnector.execute_query(create_query, [], True, False)

        if self._id is None:
            additional_query_str = ', NULL' if module_id is None else f', {module_id}'
            insert_query = f'''
                insert into version (name, const_diversities_coordinates, 
                dynamic_diversities_coordinates, reliability, module) values (
                    {self.version.name}, 
                    {json.dumps({self.formal_json_db_lst_name: self.version.const_diversities})}, 
                    {json.dumps({self.formal_json_db_lst_name: self.version.dynamic_diversities})},
                    {self.version._reliability}{additional_query_str});
            '''
            # Т.к. у нас возвращается список кортежей, берём первый элемент первого кортежа, т.к. id сего 1 возвращется!
            self.version._id = int(
                self.dbConnector.execute_query(insert_query, [], True)[0][0])
        else:
            update_query = f'''
                update version set name = '{self.version.name}',
                const_diversities_coordinates = '{json.dumps({self.formal_json_db_lst_name: self.version.const_diversities})}', 
                dynamic_diversities_coordinates = '{json.dumps({self.formal_json_db_lst_name: self.version.dynamic_diversities})}', 
                reliability = {self.version.reliability}, 
                module = {module_id} where id = {self.version.id};
            '''
            self.dbConnector.execute_query(update_query, [], True, False)

    def load(self):
        if not self.dbConnector.table_exists('version'):
            raise LookupError(
                f'There is no "VERSION" table in {self.dbConnector.db_name} data base. Save module data before load it.'
            )

        if self.version.id is None:
            select_query = 'select name, const_diversities_coordinates, dynamic_diversities_coordinates, reliability, module from version order by id;'
            q_set = self.dbConnector.execute_query(select_query)
            get_num_str = 'Choice version by id to load it.\n'
            for mdl in q_set:
                get_num_str += f'\n{str(mdl)}'
            get_num_str += '\n'
            chosen_id = input_num(get_num_str)
        else:
            chosen_id = self.version.id

        select_query = f'select id, name, const_diversities_coordinates, dynamic_diversities_coordinates, reliability, module from version where id = {chosen_id};'
        select_res = self.dbConnector.execute_query(select_query)

        # Т.к. у нас только 1 версия может быть найден по id, то обращаемся мы к 0-му индексу, без доп. проверок
        self.version._id = select_res[0][0]
        self.version._name = select_res[0][1]
        self.version._const_diversities = json.loads(select_res[0][2])[
            self.formal_json_db_lst_name]
        self.version._dynamic_diversities = json.loads(select_res[0][3])[
            self.formal_json_db_lst_name]
        self.version._reliability = float(select_res[0][4])

    def load_versions_2_module(self, module_id: int):
        if not isinstance(module_id, int):
            raise AttributeError(
                f'Invalid module_id parameter. Int is expected. {str(module_id)} was got.'
            )
        if not self.dbConnector.table_exists('version'):
            raise LookupError(
                f'There is no "VERSION" table in {self.dbConnector.db_name} data base. Save module data before load it.'
            )

        select_query = f'select id, name, const_diversities_coordinates, dynamic_diversities_coordinates, reliability, module from version where module = {module_id};'
        select_res = self.dbConnector.execute_query(select_query)

        result_list = []
        for res in select_res:
            tmp_ver = NVersion(res[0], res[1], json.loads(res[2])[
                self.formal_json_db_lst_name],
                               json.loads(res[3])[
                                   self.formal_json_db_lst_name],
                               float(res[4]))
            result_list.append(tmp_ver)
        return result_list
