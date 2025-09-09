from sqlalchemy.orm import Session
from faker import Faker
import random

from olibokit.models import Department, Employee

fake = Faker("fr_FR")

# ⚙️ Classe factory
class DepartmentFactory:
    def __init__(self, db: Session, auto_flush: bool = True, verbose: bool = False):
        self.db = db
        self.auto_flush = auto_flush
        self.verbose = verbose

    def create_department(self, name: str = None, parent_id: int = None) -> Department:
        name = name or f"{fake.company()}-{random.randint(1000, 9999)}"
        department = Department(name=name, parent_id=parent_id)
        self.db.add(department)

        if self.auto_flush:
            self.db.commit()
            self.db.refresh(department)

        if self.verbose:
            print(f"🏢 Département créé : {department.name} (ID: {department.id})")

        return department

    def create_employee(self, department_id: int = None, first_name: str = None,
                        last_name: str = None, email: str = None) -> Employee:
        first_name = first_name or fake.first_name()
        last_name = last_name or fake.last_name()
        email = email or f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"

        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            email=email,
            department_id=department_id
        )
        self.db.add(employee)

        if self.auto_flush:
            self.db.commit()
            self.db.refresh(employee)

        if self.verbose:
            print(f"👤 Employé : {employee.first_name} {employee.last_name} (ID: {employee.id})")

        return employee

    def create_department_and_employees(self, employee_count: int = 5,
                                        name: str = None, parent_id: int = None) -> dict:
        """
        Crée un département et plusieurs employés associés.

        Retourne :
        {
            "department": Department,
            "employees": [Employee, ...]
        }
        """
        department = self.create_department(name=name, parent_id=parent_id)
        employees = [
            self.create_employee(department_id=department.id)
            for _ in range(employee_count)
        ]

        return {"department": department, "employees": employees}
