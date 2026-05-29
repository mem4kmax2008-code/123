import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from data_module import DataModule
from models import Student


class MainWindow:
    """Главное окно приложения для управления студентами"""
    
    def __init__(self, root):
        """
        Инициализация главного окна.
        
        Параметры:
        root: корневое окно Tkinter
        """
        self.root = root
        self.root.title("Управление студентами")
        self.root.geometry("900x600")
        
        # Создаем модуль данных
        self.data_module = DataModule()
        
        # Флаг для отслеживания состояния таблицы
        self.is_table_open = False
        
        # Создаем интерфейс
        self._create_menu()
        self._create_toolbar()
        self._create_search_panel()
        self._create_table()
        self._create_status_bar()
        
        # Автоматически открываем таблицу при запуске
        self.open_table()
        
        # Закрываем соединение при закрытии окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _create_menu(self):
        """Создает главное меню приложения"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть таблицу", command=self.open_table)
        file_menu.add_command(label="Закрыть таблицу", command=self.close_table)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def _create_toolbar(self):
        """Создает панель инструментов"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Кнопки работы с таблицей
        self.btn_open_table = ttk.Button(toolbar, text="Открыть таблицу", command=self.open_table)
        self.btn_open_table.pack(side=tk.LEFT, padx=2)
        
        self.btn_close_table = ttk.Button(toolbar, text="Закрыть таблицу", command=self.close_table, state=tk.DISABLED)
        self.btn_close_table.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Кнопки работы с записями
        self.btn_add = ttk.Button(toolbar, text="Добавить", command=self.add_student)
        self.btn_add.pack(side=tk.LEFT, padx=2)
        
        self.btn_edit = ttk.Button(toolbar, text="Редактировать", command=self.edit_student)
        self.btn_edit.pack(side=tk.LEFT, padx=2)
        
        self.btn_delete = ttk.Button(toolbar, text="Удалить", command=self.delete_student)
        self.btn_delete.pack(side=tk.LEFT, padx=2)
        
        self.btn_refresh = ttk.Button(toolbar, text="Обновить", command=self.refresh_table)
        self.btn_refresh.pack(side=tk.LEFT, padx=2)
    
    def _create_search_panel(self):
        """Создает панель поиска"""
        search_frame = ttk.Frame(self.root)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Поиск по имени:").pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_students)
        
        ttk.Button(search_frame, text="Очистить", command=self.clear_search).pack(side=tk.LEFT, padx=5)
    
    def _create_table(self):
        """Создает таблицу для отображения данных"""
        # Фрейм для таблицы
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вертикальная полоса прокрутки
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Горизонтальная полоса прокрутки
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Таблица (Treeview)
        self.table = ttk.Treeview(
            table_frame,
            columns=("ID", "ФИО", "Год рождения", "Группа"),
            height=15,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.table.yview)
        hsb.config(command=self.table.xview)
        
        # Настройка колонок
        self.table.column("#0", width=0, stretch=tk.NO)
        self.table.column("ID", anchor=tk.CENTER, width=50)
        self.table.column("ФИО", anchor=tk.W, width=250)
        self.table.column("Год рождения", anchor=tk.CENTER, width=120)
        self.table.column("Группа", anchor=tk.CENTER, width=120)
        
        # Заголовки
        self.table.heading("#0", text="", anchor=tk.W)
        self.table.heading("ID", text="ID", anchor=tk.CENTER)
        self.table.heading("ФИО", text="Полное имя", anchor=tk.W)
        self.table.heading("Год рождения", text="Год рождения", anchor=tk.CENTER)
        self.table.heading("Группа", text="Группа", anchor=tk.CENTER)
        
        self.table.pack(fill=tk.BOTH, expand=True)
        
        # Привязываем двойной щелчок к редактированию
        self.table.bind("<Double-1>", lambda e: self.edit_student())
    
    def _create_status_bar(self):
        """Создает строку состояния"""
        self.status_bar = ttk.Label(
            self.root,
            text="Статус: таблица закрыта",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def open_table(self):
        """Открывает таблицу для работы"""
        try:
            self.data_module.open()
            self.is_table_open = True
            
            # Меняем состояние кнопок
            self.btn_open_table.config(state=tk.DISABLED)
            self.btn_close_table.config(state=tk.NORMAL)
            self.btn_add.config(state=tk.NORMAL)
            self.btn_edit.config(state=tk.NORMAL)
            self.btn_delete.config(state=tk.NORMAL)
            
            # Обновляем таблицу
            self.refresh_table()
            
            self.status_bar.config(text="Статус: таблица открыта")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть таблицу: {str(e)}")
    
    def close_table(self):
        """Закрывает таблицу"""
        try:
            self.data_module.close()
            self.is_table_open = False
            
            # Меняем состояние кнопок
            self.btn_open_table.config(state=tk.NORMAL)
            self.btn_close_table.config(state=tk.DISABLED)
            self.btn_add.config(state=tk.DISABLED)
            self.btn_edit.config(state=tk.DISABLED)
            self.btn_delete.config(state=tk.DISABLED)
            
            # Очищаем таблицу
            for item in self.table.get_children():
                self.table.delete(item)
            
            self.status_bar.config(text="Статус: таблица закрыта")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось закрыть таблицу: {str(e)}")
    
    def refresh_table(self):
        """Обновляет содержимое таблицы"""
        if not self.is_table_open:
            messagebox.showwarning("Предупреждение", "Таблица не открыта!")
            return
        
        try:
            # Очищаем таблицу
            for item in self.table.get_children():
                self.table.delete(item)
            
            # Получаем всех студентов
            students = self.data_module.get_all_students()
            
            # Заполняем таблицу
            for student in students:
                self.table.insert(
                    "",
                    tk.END,
                    values=(
                        student.id,
                        student.full_name,
                        student.birth_year or "—",
                        student.group_name or "—"
                    )
                )
            
            # Обновляем строку состояния
            count = len(students)
            self.status_bar.config(
                text=f"Статус: таблица открыта | Всего записей: {count}"
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить таблицу: {str(e)}")
    
    def search_students(self, event=None):
        """Поиск студентов по имени"""
        if not self.is_table_open:
            return
        
        search_text = self.search_entry.get().strip()
        
        try:
            # Очищаем таблицу
            for item in self.table.get_children():
                self.table.delete(item)
            
            if search_text:
                # Поиск по имени
                students = self.data_module.find_students_by_name(search_text)
                status_text = f"Найдено записей: {len(students)}"
            else:
                # Показываем всех студентов
                students = self.data_module.get_all_students()
                status_text = f"Всего записей: {len(students)}"
            
            # Заполняем таблицу
            for student in students:
                self.table.insert(
                    "",
                    tk.END,
                    values=(
                        student.id,
                        student.full_name,
                        student.birth_year or "—",
                        student.group_name or "—"
                    )
                )
            
            self.status_bar.config(text=f"Статус: таблица открыта | {status_text}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске: {str(e)}")
    
    def clear_search(self):
        """Очищает поле поиска"""
        self.search_entry.delete(0, tk.END)
        self.search_students()
    
    def add_student(self):
        """Добавляет нового студента"""
        if not self.is_table_open:
            messagebox.showwarning("Предупреждение", "Таблица не открыта!")
            return
        
        result = self._show_student_dialog("Добавить студента")
        if result:
            try:
                self.data_module.add_student(
                    full_name=result['full_name'],
                    birth_year=result['birth_year'],
                    group_name=result['group_name']
                )
                self.refresh_table()
                messagebox.showinfo("Успех", "Студент успешно добавлен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить студента: {str(e)}")
    
    def edit_student(self):
        """Редактирует выбранного студента"""
        if not self.is_table_open:
            messagebox.showwarning("Предупреждение", "Таблица не открыта!")
            return
        
        # Получаем выбранную строку
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите студента для редактирования!")
            return
        
        item = selection[0]
        student_id = int(self.table.item(item)['values'][0])
        
        try:
            # Получаем данные студента
            student = self.data_module.get_student_by_id(student_id)
            if not student:
                messagebox.showerror("Ошибка", "Студент не найден!")
                return
            
            # Показываем диалог редактирования
            result = self._show_student_dialog("Редактировать студента", student)
            if result:
                self.data_module.update_student(
                    student_id,
                    full_name=result['full_name'],
                    birth_year=result['birth_year'],
                    group_name=result['group_name']
                )
                self.refresh_table()
                messagebox.showinfo("Успех", "Данные студента обновлены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отредактировать студента: {str(e)}")
    
    def _show_student_dialog(self, title, student=None):
        """
        Вспомогательный метод для создания диалога добавления/редактирования студента.
        
        Параметры:
        title: заголовок диалога
        student: объект студента (для редактирования) или None (для добавления)
        
        Возвращает:
        dict: словарь с полями {full_name, birth_year, group_name} или None при отмене
        """
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        result = {'full_name': None, 'birth_year': None, 'group_name': None}
        
        # ФИО
        ttk.Label(dialog, text="Полное имя *").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        entry_full_name = ttk.Entry(dialog, width=30)
        entry_full_name.grid(row=0, column=1, padx=10, pady=10)
        if student:
            entry_full_name.insert(0, student.full_name)
        
        # Год рождения
        ttk.Label(dialog, text="Год рождения").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        entry_birth_year = ttk.Entry(dialog, width=30)
        entry_birth_year.grid(row=1, column=1, padx=10, pady=10)
        if student and student.birth_year:
            entry_birth_year.insert(0, str(student.birth_year))
        
        # Группа
        ttk.Label(dialog, text="Группа").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        entry_group_name = ttk.Entry(dialog, width=30)
        entry_group_name.grid(row=2, column=1, padx=10, pady=10)
        if student and student.group_name:
            entry_group_name.insert(0, student.group_name)
        
        # Обработчик сохранения
        def save():
            full_name = entry_full_name.get().strip()
            
            # Валидация
            if not full_name:
                messagebox.showwarning("Ошибка валидации", "ФИО обязательно!")
                return
            
            birth_year_str = entry_birth_year.get().strip()
            birth_year = None
            if birth_year_str:
                try:
                    birth_year = int(birth_year_str)
                except ValueError:
                    messagebox.showwarning("Ошибка валидации", "Год рождения должен быть числом!")
                    return
            
            group_name = entry_group_name.get().strip() or None
            
            result['full_name'] = full_name
            result['birth_year'] = birth_year
            result['group_name'] = group_name
            
            dialog.destroy()
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Сохранить", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        self.root.wait_window(dialog)
        
        return result if result['full_name'] else None
    
    def delete_student(self):
        """Удаляет выбранного студента"""
        if not self.is_table_open:
            messagebox.showwarning("Предупреждение", "Таблица не открыта!")
            return
        
        # Получаем выбранную строку
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите студента для удаления!")
            return
        
        # Запрашиваем подтверждение
        item = selection[0]
        student_name = self.table.item(item)['values'][1]
        
        if messagebox.askyesno("Подтверждение", f"Удалить студента '{student_name}'?"):
            try:
                student_id = int(self.table.item(item)['values'][0])
                self.data_module.delete_student(student_id)
                self.refresh_table()
                messagebox.showinfo("Успех", "Студент успешно удален!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить студента: {str(e)}")
    
    def show_about(self):
        """Показывает информацию о программе"""
        messagebox.showinfo(
            "О программе",
            "Управление студентами\n\n"
            "Версия 1.0\n"
            "Приложение для управления базой данных студентов\n\n"
            "Технологии: Python, SQLAlchemy, Tkinter"
        )
    
    def on_closing(self):
        """Обработчик закрытия приложения"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            try:
                if self.is_table_open:
                    self.data_module.close()
            except:
                pass
            self.root.destroy()


# Главная программа
if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()