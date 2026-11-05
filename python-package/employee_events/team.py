# Import the QueryBase class
from .query_base import QueryBase

# Import dependencies for sql execution # (`QueryMixin` is inherited
# through `QueryBase`, so the # `query` and `pandas_query` methods are
# available on `self`)


# Create a subclass of QueryBase # called  `Team`
class Team(QueryBase):
    name = "team"

    def names(self):
        return self.query(""" SELECT team_name, team_id
            FROM team
            ORDER BY team_id """)

    def username(self, id):
        return self.query(f""" SELECT team_name
            FROM team
            WHERE team_id = {id} """)

    def model_data(self, id):
        return self.pandas_query(
            f"""
            SELECT positive_events, negative_events
            FROM (
                SELECT employee_id,
                       SUM(positive_events) positive_events,
                       SUM(negative_events) negative_events
                FROM {self.name}
                JOIN employee_events USING({self.name}_id)
                WHERE {self.name}.{self.name}_id = {id}
                GROUP BY employee_id
            )
            """
        )
