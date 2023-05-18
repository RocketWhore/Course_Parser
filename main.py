from classes import HeadHunter, SuberJob, Connector


def main():
    vacancies_js = []

    keyword = 'Python'

    hh = HeadHunter(keyword)
    sj = SuberJob(keyword)
    # print(hh.get_requests())
    for api in (hh, sj):
        api.get_vacancies(pages_count=2)
        vacancies_js.extend(api.get_formated_vacancies())

    connector = Connector(keyword=keyword, vacancies_json=vacancies_js)
    while True:
        command = input(
            'v - Вывести список вакансий;\n'
            'min - Отсортировать вакансии по минимальной зарплате;\n'
            'max - Отсортровать вакансии по максимальной зарплатк;\n'
            'exit - Для выхода.\n'

        )
        if command.lower() == 'exit':
            break
        elif command.lower() == 'v':
            vacancies = connector.select()
        elif command.lower() == 'min':
            vacancies = connector.sorted_vacancies_by_salary_from()
        elif command.lower() == 'max':
            vacancies = connector.sorted_vacancies_by_salary_to()

        vacancies = connector.select()

        for vacancy in vacancies:
            print(vacancy, end='\n\n')


if __name__ == '__main__':
    main()
