
# Import the QueryBase class
from .query_base import QueryBase


# Define a subclass of QueryBase called Employee
class Employee(QueryBase):
    name = "employee"

    def names(self):
        return self.query(
            """
            SELECT first_name || ' ' || last_name AS full_name,
                   employee_id
            FROM employee
            ORDER BY employee_id
            """
        )

    # Define a method called username
    def username(self, id):
        return self.query(
            f"""
            SELECT first_name || ' ' || last_name AS full_name
            FROM employee
            WHERE employee_id = {id}
            """
        )

    # The SQL query
    def model_data(self, id):
        return self.pandas_query(
            f"""
            SELECT SUM(positive_events) positive_events,
                   SUM(negative_events) negative_events
            FROM {self.name}
            JOIN employee_events USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
            """
        )
