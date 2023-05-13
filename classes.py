import requests
import os
from abc import ABC, abstractmethod
import json
from pprint import pprint


class ParsingError(Exception):
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
        salary_from = f'От {self.salary_from}' if self.salary_from else ''
        salary_from = f'До {self.salary_to}' if self.salary_to else ''
        if self.salary_from is None and self.salary_to is None:
            salary_from = 'Не указана'
        return f'Вакансия: \"{self.title}\" \nКомпания: \"{self.employer}\" \nЗарплата: \"{self.salary_from} {self.salary_to}\" \nURL: \"{self.url}\"'


class Connector:
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
        formated_salary = [None, None]
        if salary and salary['from'] and salary['from'] != 0:
            formated_salary[0] = salary['from'] if salary['currency'].lower() == 'rur' else salary['from'] * 78
        if salary and salary['to'] and salary['to'] != 0:
            formated_salary[1] = salary['to'] if salary['currency'].lower() == 'rur' else salary['to'] * 78
        return formated_salary
    def get_requests(self):
        response = requests.get('https://api.hh.ru/vacancies',
                                headers=self.__header,
                                params=self.__params)
        if response.status_code != 200:
            raise ParsingError

        return response.json()['items']

    def get_formated_vacancies(self):
        formated_vacancies = []
        for vacancy in self.__vacancies:
            salary_from, salary_to = self.get_salary(vacancy['salary'])
            formated_vacancies.append({
                'id': vacancy['id'],
                'title': vacancy['title'],
                'url': vacancy['url'],
                'salary_from': salary_from,
                'salary_to': salary_to,
                'employer': vacancy['employer']['name'],
                'api': 'HeadHunter'
            })
        return formated_vacancies

    def get_vacancies(self, pages_count=1):
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
    pass


hh = HeadHunter('Python')
pprint(hh)
