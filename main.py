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

    vacancies = connector.select()

    for vacancy in vacancies:
        print(vacancy, end='\n\n')


if __name__ == '__main__':
    main()
