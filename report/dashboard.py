# from fasthtml.common import *
from fasthtml.common import FastHTML, H1, Div, serve
import matplotlib.pyplot as plt

# Import QueryBase, Employee, Team from employee_events
from employee_events import Employee, Team

# import the load_model function from the utils.py file
from utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
)

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown # called `ReportDropdown`
class ReportDropdown(Dropdown):
    def build_component(self, entity_id, model):
        # Set the `label` attribute so it is set #  to the `name` attribute for
        # the model
        self.label = model.name
        # Return the output from the # parent class's build_component method
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        return model.names()


# Create a subclass of base_components/BaseComponent # called `Header`
class Header(BaseComponent):
    def build_component(self, entity_id, model):
        return H1(model.name)


# Create a subclass of base_components/MatplotlibViz
# called `LineChart`
class LineChart(MatplotlibViz):
    def visualization(self, entity_id, model):
        # Pass the `asset_id` argument to# the model's `event_counts` method to
        # # receive the x (Day) and y (event count)
        df = model.event_counts(entity_id)
        df = df.fillna(0)
        df = df.set_index('event_date')
        df = df.sort_index()
        df = df.cumsum()
        df.columns = ['Positive', 'Negative']
        fig, ax = plt.subplots()
        df.plot(ax=ax)
        self.set_axis_styling(ax, bordercolor='blue', fontcolor='blue')
        ax.set_title('Cumulative Events by Day', fontsize=20)
        ax.set_xlabel('Day')
        ax.set_ylabel('Cumulative Event Count')


class BarChart(MatplotlibViz):
    predictor = load_model()

    def visualization(self, entity_id, model):
        data = model.model_data(entity_id)
        probabilities = self.predictor.predict_proba(data)
        probabilities = probabilities[:, 1]
        if model.name == "team":
            pred = probabilities.mean()
        else:
            pred = probabilities[0]
        fig, ax = plt.subplots()
        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')


# Create a subclass of combined_components/CombinedComponent # called
# Visualizations
class Visualizations(CombinedComponent):
    children = [LineChart(), BarChart()]
    outer_div_type = Div(cls='grid')

# Create a subclass of base_components/DataTable # called `NotesTable`


class NotesTable(DataTable):
    def component_data(self, entity_id, model):
        return model.notes(entity_id)


class DashboardFilters(FormGroup):
    id = "top-filters"
    action = "/update_data"
    method = "POST"
    children = [Radio(values=["Employee", "Team"], name='profile_type',
                      hx_get='/update_dropdown', hx_target='#selector'),
                ReportDropdown(id="selector", name="user-selection")]

# Create a subclass of CombinedComponents # called `Report`


class Report(CombinedComponent):
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]


# Initialize a fasthtml app
app = FastHTML()

# Initialize the `Report` class
report = Report()


# Create a route for a get request # Set the route's path to the root
@app.get('/')
def index():
    return report(1, Employee())


@app.get('/employee/{id}')
def employee(id: str):
    return report(id, Employee())


@app.get('/team/{id}')
def team(id: str):
    return report(id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)


serve()
