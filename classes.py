import requests
import os
from abc import ABC, abstractmethod
import json
from pprint import pprint


class ParsingError(Exception):
    '''Искусственная ошибка при ошибке парсинга'''
    def __str__(self):
        return 'Ошибка парсинга данных'


class Vacancy:
    __slots__ = ('id', 'title', 'url', 'salary_from', 'salary_to', 'employer', 'api')

    def __init__(self, vacancy_id, title, url, salary_from, salary_to, employer, api):
        self.id = vacancy_id
        self.title = title
        self.url = url
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.employer = employer
        self.api = api

    def __gt__(self, other):
        if not other.salary_min:
            return True
        elif not self.salary_from:
            return False

    def __str__(self):
        salary_from = f'От {self.salary_from}' if self.salary_from != None else ''
        salary_to = f'До {self.salary_to}' if self.salary_to != None else ''
        if self.salary_from is None and self.salary_to is None:
            salary_from = 'Не указана'
        return f'Вакансия: \"{self.title}\" \nКомпания: \"{self.employer}\" \nЗарплата: \"{salary_from} {salary_to}\" \nURL: \"{self.url}\"'


class Connector:
    '''Класс, в котором происходит запись и чтение файла с вакансиями'''
    def __init__(self, keyword, vacancies_json):
        self.__filename = f'{keyword.title()}.json'
        self.insert(vacancies_json)

    def insert(self, vacancies_json):
        with open(self.__filename, 'w', encoding='utf-8') as file:
            json.dump(vacancies_json, file, ensure_ascii=False, indent=4)

    def select(self):
        with open(self.__filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        vacancies = [Vacancy(x['id'], x['title'], x['url'], x['salary_from'], x['salary_to'], x['employer'], x['api'])
                     for x in data]
        return vacancies


class Engine(ABC):

    @abstractmethod
    def get_requests(self):
        pass

    def get_vacancies(self):
        pass


class HeadHunter(Engine):
    '''Класс для получения вакансий'''
    def __init__(self, keyword):
        self.__header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
        }
        self.__params = {
            'text': keyword,
            'page': 0,
            'per_page': 100
        }
        self.__vacancies = []

    @staticmethod
    def get_salary(salary):
        '''Метод определения зарплаты вакансии'''
        formated_salary = [None, None]
        if salary and salary['from'] and salary['from'] != 0:
            formated_salary[0] = salary['from'] if salary['currency'].lower() == 'rur' else salary['from'] * 78
        if salary and salary['to'] and salary['to'] != 0:
            formated_salary[1] = salary['to'] if salary['currency'].lower() == 'rur' else salary['to'] * 78
        return formated_salary
    def get_requests(self):
        '''Метод для получения данных с сайта вакансий hh.ru'''
        response = requests.get('https://api.hh.ru/vacancies',
                                headers=self.__header,
                                params=self.__params)
        if response.status_code != 200:
            raise ParsingError

        return response.json()['items']

    def get_formated_vacancies(self):
        '''Метод для форматирования вакансий'''
        formated_vacancies = []
        for vacancy in self.__vacancies:
            salary_from, salary_to = self.get_salary(vacancy['salary'])
            formated_vacancies.append({
                'id': vacancy['id'],
                'title': vacancy['name'],
                'url': vacancy['url'],
                'salary_from': salary_from,
                'salary_to': salary_to,
                'employer': vacancy['employer']['name'],
                'api': 'HeadHunter'
            })
        return formated_vacancies

    def get_vacancies(self, pages_count=1):
        '''Метод для получения вакансий'''
        while self.__params['page'] < pages_count:
            print(f'HeadHunter. Идет парсинг {self.__params["page"] + 1}', end=': ')
            try:
                values = self.get_requests()
            except ParsingError:
                print('ParsingError')
                break
            print(f'Найдено {len(values)} вакансий!')
            self.__vacancies.extend(values)

            self.__params['page'] += 1
            # pprint(self.__vacancies)
            # exit()
        return self.__vacancies

class SuberJob(Engine):
    '''Класс для получения вакансий'''
    def __init__(self, keyword, page=1):
        self.__url = 'https://api.superjob.ru/2.0/vacancies/'
        self.__params = {
            'keyword': keyword,
            'page': page,
            'count': 100
        }
        self.__vacancies = []

    @staticmethod
    def get_salary(salary, currency):
        '''Метод определения зарплаты вакансии'''
        formated_salary = None
        if salary in salary != 0:
            formated_salary = salary if currency == 'rub' else salary * 78
        return formated_salary

    def get_requests(self):
        '''Метод для получения данных с сайта вакансий Superjob.ru'''
        headers = {'X-Api-App-Id': 'v3.r.137548631.f544406f5907a6b8e70a9c04926148fe40d98de7.9fe68dddad34b77d2c0e32c55e764fae58e1a56d'}
        response = requests.get(url=self.__url, headers=headers, params=self.__params)
        # if response.status_code != 200:
        #     raise ParsingError
        return response.json()['objects']

    def get_formated_vacancies(self):
        '''Метод для форматирования вакансий'''
        formated_vacancies = []
        for vacancy in self.__vacancies:
            formated_vacancies.append({
                'id': vacancy['id'],
                'title': vacancy['profession'],
                'url': vacancy['link'],
                'salary_from': self.get_salary(vacancy['payment_from'], vacancy['currency']),
                'salary_to': self.get_salary(vacancy['payment_to'], vacancy['currency']),
                'employer': vacancy['firm_name'],
                'api': 'SuperJob'
            })
        return formated_vacancies

    def get_vacancies(self, pages_count=1):
        '''Метод для получения вакансий'''
        while self.__params['page'] < pages_count:
            print(f'SuperJob. Идет парсинг {self.__params["page"] + 1}', end=': ')
            try:
                values = self.get_requests()
            except ParsingError:
                print('ParsingError')
                break
            print(f'Найдено {len(values)} вакансий!')
            self.__vacancies.extend(values)

            self.__params['page'] += 1
            # pprint(self.__vacancies)
            # exit()
        return self.__vacancies

# hh = HeadHunter('Python')
# pprint(hh)
sj = SuberJob('Python')
pprint(sj.get_requests())