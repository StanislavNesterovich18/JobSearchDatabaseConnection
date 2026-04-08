from os import getenv  # type: ignore

from dotenv import load_dotenv

from src.api_classes import ApiClass, Employer
from src.db_manager import DBManager

load_dotenv()
DB_NAME = getenv("DB_NAME")
DB_HOST = getenv("DB_HOST")
DB_PORT = getenv("DB_PORT", 5432)
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")

api = ApiClass()

list_employees_id = {
    "Avito": "84585",
    "Точка банк": "2324020",
    "Купер": "1272486",
    "Aston": "6093775",
    "VK": "15478",
    "Контур": "41862",
    "Тензор": "67611",
    "Яндекс": "1740",
    "2ГИС": "64174",
    "Skyeng": "1122462",
}
data: list[Employer] = api.get_list_employees(list_employees_id)
DBManager.db_create(DB_PASSWORD, DB_NAME)
db_man = DBManager(DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD)
db_man.create_table()
db_man.insert_company(data)


def interact_user() -> None:
    """Функция взаимодействия с пользователем"""
    print("Список компаний: ")
    for i, employee in enumerate(list_employees_id.keys(), start=1):
        print(f"{i}. {employee}")
    while True:
        print("Выберите один из пунктов меню: ")
        user_input = input("""
1. Получить список всех компаний и количество вакансий. 
2. Получить список всех вакансий  
3. Получить среднюю зарплату по вакансиям. 
4. Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям. 
5. Поиск вакансий по ключевому слову.\n""")

        if user_input == "1":
            company_vacancy = db_man.get_companies_and_vacancies_count()
            for company, count_vac in company_vacancy:
                print(f"Компания: {company} \nКоличество вакансий: {count_vac}")
        elif user_input == "2":
            all_vacancy = db_man.get_all_vacancies()
            for company, vacancy_name, salary, url in all_vacancy:
                print(f"Компания: {company} \nНазвание вакансии: {vacancy_name}\nЗарплата: {salary} \nСсылка: {url}")
        elif user_input == "3":
            avg_salary = db_man.get_avg_salary()
            print("Средняя зарплата:", avg_salary, "руб.")
        elif user_input == "4":
            vacancy_higher_salary = db_man.get_vacancies_with_higher_salary()
            for company in vacancy_higher_salary:
                print(f"Вакансия: {company[2]} {company[4]} - {company[5]} \nОписание вакансии: {company[6]}")
        elif user_input == "5":
            word_input = input("Ведите ключевое слово: \n")
            vacancy_keyword = db_man.get_vacancies_with_keyword(word_input)
            for company in vacancy_keyword:
                print(f"Вакансия: {company[2]} {company[4]} - {company[5]} \nОписание вакансии: {company[6]}")


if __name__ == "__main__":
    interact_user()
