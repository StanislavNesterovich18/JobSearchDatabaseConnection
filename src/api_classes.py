from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import requests
from requests import Response


@dataclass
class Vacancies:
    """Класс для работы с вакансиями"""

    id: str
    name: str
    salary_from: int
    apply_alternate_url: str
    snippet_requirement: str
    salary_to: int | None = None


@dataclass
class Employer:
    """Класс для работы с работодателями"""

    id: str
    name: str
    description: str
    alternate_url: str
    list_vacancies: list[Vacancies] = field(default_factory=list)


class BaseApiClass(ABC):
    """Абстрактный класс для работы с API сервиса с вакансиями."""

    @abstractmethod
    def _connect(self) -> None: ...

    @abstractmethod
    def get_list_employees(self, list_employees: dict[str, str]) -> list[Employer]: ...

    @abstractmethod
    def get_info_employer(self, employer_id: str) -> Employer: ...
    @abstractmethod
    def get_info_vacancies(self, vacancies_url_employer: str) -> list[Vacancies]: ...


class ApiClass(BaseApiClass):
    """Класс для работы с Апи запросами"""

    __BASE_URL = "https://api.hh.ru/"

    def __init__(self) -> None:
        self.__session = requests.Session()
        self.__headers = {"User-Agent": "HH-User-Agent"}
        self._connect()

    def _connect(self) -> None:
        """Метод для проверки соединения по Апи запросу"""
        test_connect: Response = self.__session.get(self.__BASE_URL + "vacancies", headers=self.__headers)
        test_connect.raise_for_status()

    def get_list_employees(self, list_employees: dict[str, str]) -> list[Employer]:
        """Метод дабавления выборки информации о работодателе в список"""
        employees: list[Employer] = []
        for name_employer, id_employer in list_employees.items():
            info_employer = self.get_info_employer(id_employer)
            employees.append(info_employer)

        return employees

    def get_info_employer(self, employer_id: str) -> Employer:
        """Метод выборки данных о работодателе"""
        response = self.__session.get(self.__BASE_URL + f"employers/{employer_id}", headers=self.__headers)
        response.raise_for_status()
        info_employer = response.json()
        print(info_employer)
        id_employer: str = info_employer["id"]
        name_employer: str = info_employer["name"]
        description_employer: str = info_employer["description"]
        alternate_url_employer: str = info_employer["alternate_url"]
        vacancies_url_employer: str = info_employer["vacancies_url"]
        list_vacancies: list[Vacancies] = self.get_info_vacancies(vacancies_url_employer)
        return Employer(
            id=id_employer,
            name=name_employer,
            description=description_employer,
            alternate_url=alternate_url_employer,
            list_vacancies=list_vacancies,
        )

    def get_info_vacancies(self, vacancies_url_employer: str) -> list[Vacancies]:
        """Метод выборки данных о вакансия работодателя"""
        params: dict = {"only_with_salary": True}
        response: Response = self.__session.get(vacancies_url_employer, params=params, headers=self.__headers)
        list_vacancies: list[Vacancies] = [
            Vacancies(
                id=item["id"],
                name=item["name"],
                salary_from=item["salary"]["from"],
                salary_to=item["salary"]["to"],
                apply_alternate_url=item["apply_alternate_url"],
                snippet_requirement=item["snippet"]["requirement"],
            )
            for item in response.json()["items"]
        ]
        return list_vacancies
