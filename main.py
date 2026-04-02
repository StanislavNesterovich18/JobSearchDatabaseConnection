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

if __name__ == "__main__":
    data: list[Employer] = api.get_list_employees(list_employees_id)

    DBManager.db_create(DB_PASSWORD, DB_NAME)
    db_man = DBManager(DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD)
    print(DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD)
    # db_man.connect()
    db_man.create_table()
    db_man.insert_company(data)
    print(db_man.get_vacancies_with_keyword("python"))

# абстрактный класс, doc
