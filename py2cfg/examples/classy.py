class Employee:
    """Common base class for all employees"""

    empCount = 0

    def __init__(self, name, salary):
        print("creating")
        self.name = name
        self.salary = salary
        Employee.empCount += 1
        # type(self).empCount += 1

    def displayCount(self):
        print("Total Employee %d" % Employee.empCount)

    def displayEmployee(self):
        print("Name : ", self.name, ", Salary: ", self.salary)

    def __str__(self):
        return "Name : " + self.name + ", Salary: " + str(self.salary)

    def __del__(self):
        print("takin out the trash")
        type(self).empCount -= 1


"""
You normally will not notice when the garbage collector destroys an orphaned instance and reclaims its space.
But a class can implement the special method __del__(), called a destructor, that is invoked when the instance is about to be destroyed.
This method might be used to clean up any non memory resources used by an instance.
"""

if 5 < 10:
    emp1 = Employee(name="Bob", salary=2000)
emp2 = Employee("Jed", 5000)
emp1.name
emp1.displayEmployee()
emp2.displayEmployee()
print("Total Employee %d" % Employee.empCount)
emp1 = emp2
print("Total Employee %d" % Employee.empCount)
del emp1
del emp2
