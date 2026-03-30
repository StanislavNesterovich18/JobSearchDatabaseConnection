from abc import ABC, abstractmethod
from typing import Any

import psycopg2
import psycopg2 as psycopg
from psycopg2._psycopg import connection

from src.api_classes import Employer


class BaseDBManager(ABC):
    """Абстрактный метод для всех классов подключений к БД"""

    @abstractmethod
    def create_table(self) -> None: ...


class DBManager(BaseDBManager):
    __slots__ = (
        "db_name",
        "db_host",
        "db_port",
        "db_user",
        "db_password",
    )

    def __init__(self, db_name: str, db_host: str, db_port: int, db_user: str, db_password: str):
        self.__db_name = db_name
        self.__db_host = db_host
        self.__db_port = db_port
        self.__db_user = db_user
        self.__db_password = db_password
        self.__conn: connection = psycopg.connect(
            dbname=self.__db_name,
            user=self.__db_user,
            password=self.__db_password,
            port=self.__db_port,
            host=self.__db_host,
        )

    @staticmethod
    def db_create(
        db_password: str, db_name: str, db_user: str = "postgres", db_port: int = 5432, db_host: str = "127.0.0.1"
    ) -> None:
        conn = psycopg.connect(dbname="postgres", user=db_user, password=db_password, port=db_port, host=db_host)
        conn.set_session(autocommit=True)
        cursor = conn.cursor()
        cursor.execute(
            """
                    SELECT EXISTS(
                        SELECT 1 
                        FROM pg_database 
                        WHERE datname IN (
                            SELECT %s::text
                        )
                    )
                """,
            (db_name,),
        )
        exists: tuple[Any] | None = cursor.fetchone()

        if exists and not exists[0]:
            cursor.execute(f"CREATE DATABASE {db_name}")

    def create_table(self) -> None:
        if self.__conn is None:
            self._connect()
        conn = psycopg.connect(
            dbname=self.__db_name,
            user=self.__db_user,
            password=self.__db_password,
            port=self.__db_port,
            host=self.__db_host,
        )
        conn.set_session(autocommit=True)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies 
            (
                id INT PRIMARY KEY,
                name TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacancies 
            (
                id_vacancy INT PRIMARY KEY,
                company_id INT REFERENCES companies(id) NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                salary_from INT,
                salary_to INT,
                requirement TEXT 
            );
        """)

    def _connect(self) -> None:
        try:
            self.__conn = psycopg.connect(
                dbname=self.__db_name,
                user=self.__db_user,
                password=self.__db_password,
                port=self.__db_port,
                host=self.__db_host,
            )
            if self.__conn:
                self.__conn.set_session(autocommit=True)
        except Exception as e:
            print(e)
            raise ValueError("Проверьте введенные данные.")

    def insert_company(self, employers: list[Employer]) -> None:
        if self.__conn is None:
            self._connect()
        if self.__conn is None:
            raise ValueError("Нет соединения.")
        cursor = self.__conn.cursor()
        for company in employers:
            try:
                id_company = self.get_id_company(company.id)
                if id_company is None:
                    cursor.execute(f"""
                       INSERT INTO companies(id, name) VALUES ({company.id}, '{company.name}') RETURNING id;
                    """)
                    fetch_data: tuple[int] | None = cursor.fetchone()
                    id_company = fetch_data[0] if fetch_data else None
                for vacancy in company.list_vacancies:
                    is_exist_vacancy = self.exist_vacancy(id_company, vacancy.id)
                    if is_exist_vacancy:
                        cursor.execute(f"""
                                INSERT INTO vacancies
                                (
                                id_vacancy,
                                company_id,
                                name,
                                url,
                                salary_from,
                                salary_to,
                                requirement
                                ) VALUES (
                                {vacancy.id},
                                {id_company},
                                '{vacancy.name}',
                                '{vacancy.apply_alternate_url}',
                                {vacancy.salary_from or 0},
                                {vacancy.salary_to or 0},
                                '{vacancy.snippet_requirement}'
                                 );
                            """)
            except Exception as e:
                print(company, e)

    def exist_vacancy(self, company_id: int | None, id_vacancy: str) -> bool:
        if not isinstance(company_id, int):
            raise ValueError("Такой компании не найдено")
        if self.__conn is None:
            self._connect()
        cursor = self.__conn.cursor()
        cursor.execute(f"""
            SELECT  
                id_vacancy,
                company_id 
            FROM 
                vacancies 
            WHERE 
                id_vacancy = {id_vacancy} 
            AND 
                company_id = {company_id};
        """)
        get_data = cursor.fetchone()
        return get_data is None

    def get_id_company(self, company_id: str) -> int | None:
        if self.__conn is None:
            self._connect()
        cursor = self.__conn.cursor()
        cursor.execute(f"""
            SELECT  
                id 
            FROM 
                companies
            WHERE 
                id = {company_id};
        """)
        get_data: tuple | None = cursor.fetchone()
        return get_data[0] if get_data else None

    def get_companies_and_vacancies_count(self) -> list[tuple]:
        if self.__conn is None:
            self._connect()
        cursor = self.__conn.cursor()
        cursor.execute("""
            SELECT 
            companies.name, COUNT(vacancies) FROM companies 
JOIN vacancies ON vacancies.company_id=companies.id
GROUP BY companies.name
        """)
        return cursor.fetchall()

    def get_all_vacancies(self) -> list[tuple]:
        if self.__conn is None:
            self._connect()
        cursor = self.__conn.cursor()
        cursor.execute("""SELECT
             companies.name 
             AS company_name, vacancies.name 
             AS vacancy_name, vacancies.salary_from || ' - ' || vacancies.salary_to 
             AS salary, vacancies.url FROM companies 
JOIN vacancies ON vacancies.company_id=companies.id
GROUP BY companies.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
ORDER BY companies.name ASC""")
        return cursor.fetchall()

    def get_avg_salary(self) -> float:
        if self.__conn is None:
            self._connect()
        cursor = self.__conn.cursor()
        cursor.execute("""
        SELECT
            (AVG(vacancies.salary_from) +  AVG(vacancies.salary_to))/2 
        AS avg_salary FROM vacancies""")
        avg_salary: tuple | None = cursor.fetchone()
        return round(avg_salary[0], 2) if avg_salary else 0

    def get_vacancies_with_higher_salary(self) -> list[tuple]:
        if self.__conn is None:
            self._connect()
        cursor = self.__conn.cursor()
        avg_salary = self.get_avg_salary()
        cursor.execute(f"""SELECT * FROM vacancies WHERE salary_to > {avg_salary}""")
        return cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> list[tuple]:
        if self.__conn is None:
            self._connect()
        cursor = self.__conn.cursor()
        cursor.execute(f"""
            SELECT * FROM vacancies WHERE name iLIKE '%{keyword}%'
        """)
        return cursor.fetchall()
