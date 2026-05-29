# data_module.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Student

class DataModule:    
    def __init__(self, db_path="database/students.db"):
        """
        Инициализация модуля данных.
        
        Параметры:
        db_path (str): путь к файлу базы данных
        """
        # Создаем папку для БД, если её нет
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Создаем движок SQLAlchemy (аналог настройки BDE Alias)
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Создаем таблицы, если их нет
        Base.metadata.create_all(self.engine)
        
        # Создаем фабрику сессий
        self.Session = sessionmaker(bind=self.engine)
        
        # Текущая сессия (будет создана при необходимости)
        self._current_session = None
        self._is_open = False
    
    @property
    def is_open(self):
        """Свойство, показывающее, открыта ли сессия (аналог Table.Active)"""
        return self._is_open
    
    def open(self):
        """Открыть сессию для работы с данными (аналог Table.Active = True)"""
        if not self._current_session:
            self._current_session = self.Session()
            self._is_open = True
        return self._current_session
    
    def close(self):
        """Закрыть сессию (аналог Table.Active = False)"""
        if self._current_session:
            self._current_session.close()
            self._current_session = None
            self._is_open = False
    
    def get_session(self):
        """Получить текущую сессию (если не открыта - открыть автоматически)"""
        if not self._is_open:
            self.open()
        return self._current_session
    
    # ----- CRUD операции (аналоги методов работы с таблицей) -----
    
    def get_all_students(self):
        """
        Получить всех студентов.
        Аналог: открытая таблица в режиме просмотра.
        """
        session = self.get_session()
        return session.query(Student).all()
    
    def get_student_by_id(self, student_id):
        """Получить студента по ID"""
        session = self.get_session()
        return session.query(Student).filter_by(id=student_id).first()
    
    def add_student(self, full_name, birth_year=None, group_name=None):
        """
        Добавить нового студента.
        Аналог: Table.Insert + Post.
        
        Параметры:
        full_name (str): ФИО студента (обязательно)
        birth_year (int): год рождения (необязательно)
        group_name (str): группа (необязательно)
        
        Возвращает:
        Student: созданный объект студента
        """
        session = self.get_session()
        new_student = Student(
            full_name=full_name,
            birth_year=birth_year,
            group_name=group_name
        )
        session.add(new_student)
        session.commit()
        return new_student
    
    def update_student(self, student_id, **kwargs):
        """
        Обновить данные студента.
        Аналог: Table.Edit + Post.
        
        Параметры:
        student_id (int): ID студента
        **kwargs: поля для обновления (full_name, birth_year, group_name)
        
        Возвращает:
        Student: обновленный объект или None, если студент не найден
        """
        session = self.get_session()
        student = session.query(Student).filter_by(id=student_id).first()
        if student:
            for key, value in kwargs.items():
                if hasattr(student, key):
                    setattr(student, key, value)
            session.commit()
        return student
    
    def delete_student(self, student_id):
        """
        Удалить студента.
        Аналог: Table.Delete.
        
        Возвращает:
        bool: True если удаление успешно, False если студент не найден
        """
        session = self.get_session()
        student = session.query(Student).filter_by(id=student_id).first()
        if student:
            session.delete(student)
            session.commit()
            return True
        return False
    
    def find_students_by_name(self, name_part):
        """
        Поиск студентов по части имени.
        Аналог: Locate или Filter.
        """
        session = self.get_session()
        return session.query(Student).filter(
            Student.full_name.contains(name_part)
        ).all()
    
    def get_students_count(self):
        """Получить общее количество студентов"""
        session = self.get_session()
        return session.query(Student).count()
    
    def get_students_by_group(self, group_name):
        """
        Получить всех студентов указанной группы.
        Задание для самостоятельной работы - метод 4.
        
        Параметры:
        group_name (str): название группы
        
        Возвращает:
        list: список студентов группы
        """
        session = self.get_session()
        return session.query(Student).filter_by(group_name=group_name).all()