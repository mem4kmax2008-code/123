from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Базовый класс для всех моделей
Base = declarative_base()

class Student(Base):
    """
    Модель студента.
    Соответствует таблице students в базе данных.
    """
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    birth_year = Column(Integer)
    group_name = Column(String(20))
    
    def __repr__(self):
        return f"Студент: {self.full_name} (группа {self.group_name})"