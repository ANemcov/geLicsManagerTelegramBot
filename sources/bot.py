# from sources.main import Settings
import requests
import json
from requests import HTTPError

Settings = None


class GrotemServerConnector(object):

    def __init__(self, url='', password=''):
        self._server_url = url
        self._server_password = password
        self.error_code = 0
        self.error_description = ''
        self.message = ''
        self.data = None

    def _init_error_info(self):
        self.error_code = 0
        self.error_description = ''
        self.message = ''
        self.data = None

    def _send_command(self, uri, **kwargs):
        url = self._server_url + uri
        passwd = kwargs['auth_password'] if 'auth_password' in kwargs else self._server_password

        try:
            response = requests.get(url=url, auth=('admin', passwd))
            response.raise_for_status()
        except HTTPError as http_err:
            return f'{http_err}'
        except Exception as err:
            return f'{err}'
        else:
            return response.text

    def _get_solution_password(self, solution_name):
        if solution_name is None:
            raise ValueError('Solution Name required')
        pet_password_uri = f'/system/solutions/getpassword/{solution_name}'
        result = self._send_command(pet_password_uri)
        return result

    def check_connection(self):
        self._init_error_info()
        check_uri = '/system/version'
        response = self._send_command(check_uri)
        if '(ver ' in response:
            self.error_code = 0
            self.error_description = ''
            self.data = response
            return True
        else:
            self.error_code = -1
            self.error_description = str(response)
            return False

    def get_solution_list(self):
        self._init_error_info()
        solution_list_uri = '/system/solutions'
        response = self._send_command(solution_list_uri)
        if type(response) != str:
            self.error_code = 1
            self.error_description = 'Get licenses list error: '+str(response)
            return False
        try:
            lic_list = response.split(';')
        except Exception as e:
            self.error_code = 2
            self.error_description = 'Get licenses list split error: ' + str(e)
            return False

        self.error_code = 0
        self.error_description = ''
        self.data = lic_list
        return True
    
    def get_lic_info(self, solution_name: str):
        self._init_error_info()
        if solution_name is None:
            raise ValueError('Solution Name required')

        glic_uri = f'/{solution_name}/admin/GetLicensesCount'
        solution_password = self._get_solution_password(solution_name)
        result = self._send_command(glic_uri, auth_password=solution_password)

        if type(result) != str:
            self.error_code = 1
            self.error_description = 'Get licenses error: '+str(result)
            return False

        try:
            lic_info = json.loads(result)
        except Exception as e:
            self.error_code = 2
            self.error_description = 'Get licenses error: ' + str(e)
            return False

        self.error_code = 0
        self.error_description = ''
        self.data = lic_info
        return True

    def set_lic_count(self, solution_name: str, lic_count: int):
        self._init_error_info()
        if solution_name is None:
            raise ValueError('Solution Name required')

        slic_uri = f'/system/solutions/setlicenses/{solution_name}/{lic_count}'
        result = self._send_command(slic_uri)
        if result == 'ok':
            self.error_code = 0
            self.error_description = ''
            self.data = 'ok'
        else:
            self.error_code = -1
            self.error_description = str(result)
            self.data = result

        return self.error_code == 0

    def reset_lic_count(self, solution_name: str):
        self._init_error_info()
        if solution_name is None:
            raise ValueError('Solution Name required')

        try:
            result = self.get_lic_info(solution_name)
            if result:
                lic_count = self.data['TotalLicenses']
            else:
                # Transfer error info from previous execution of self
                print(self.error_description)
                return False
        except Exception as e:
            self.error_code = -1
            self.error_description = f'Error: Invalid lic_info: {e}'
            self.data = str(e)
            print(self.error_description)
            return False

        res = self.set_lic_count(solution_name=solution_name, lic_count=lic_count)
        if res:
            self.error_code = 0
            self.error_description = ''
            self.data = 'ok'
            return True
        else:
            # Transfer error info from previous execution of self
            print(self.error_description)
            return False
