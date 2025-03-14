import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
np.float_ = np.float64
np.complex_=np.complex128
import pandas as pd
import streamlit as st
import plotly.express as px
import os

from pyomo.environ import *
from pyomo.gdp import *

def start_optimization(product_1: pd.DataFrame, product_2: pd.DataFrame, product_3: pd.DataFrame):
    # Daten für die Prozesse
    process_data = {
        'A': product_1.to_dict('records'),
        'B': product_2.to_dict('records'),
        'C': product_3.to_dict('records')
    }

    # Füge den letzten Prozess für den ersten Prozess von product_2 und product_3 hinzu
    def find_last_process(processes):
        if processes:
            return processes[-1]['Process']
        return None

    last_process_1 = find_last_process(process_data['A'])
    last_process_2 = find_last_process(process_data['B'])

    if process_data['B'] and last_process_1:
        process_data['B'][0]['Predecessor'] = [last_process_1]
    if process_data['C'] and last_process_2:
        process_data['C'][0]['Predecessor'] = [last_process_2]

    # Erstelle das Pyomo-Modell
    model = ConcreteModel()

    # Sets
    model.Products = Set(initialize=process_data.keys())
    processes = [f"{i}_{p}" for p in process_data.keys() for i in range(1, len(process_data[p]) + 1)]
    model.Processes = Set(initialize=processes)
    model.Workers = Set(initialize=['Machine Operator', 'Setter', 'Machine Operator + Setter'])

    #model.Processes.display()

    # Parameters
    def processing_time_init(model, pr, w):
        process, product = pr.split('_')
        return process_data[product][int(process)-1][f"Processing Time {w}"]
    
    def cost_init(model, pr, w):
        process, product = pr.split('_')
        return process_data[product][int(process)-1][f"Cost {w}"]

    def predecessors_init(model, pr):
        process, product = pr.split('_')
        return process_data[product][int(process)-1]["Predecessor"]

    model.ProcessingTime = Param(model.Processes, model.Workers, within=NonNegativeReals, initialize=processing_time_init)
    model.Cost = Param(model.Processes, model.Workers, within=NonNegativeReals, initialize=cost_init)
    model.Predecessors = Param(model.Processes, within=Any, initialize=predecessors_init)
    model.ProductionTime = Param(initialize=60, within=NonNegativeReals)

    # Variables
    model.StartTime = Var(model.Processes, within=NonNegativeReals, bounds=(0, 10000))
    model.EndTime = Var(model.Processes,  within=NonNegativeReals, bounds=(0, 10000))
    model.WorkerAssignment = Var(model.Processes, model.Workers, within=Binary)
    model.WorkerUsage = Var(model.Processes, within=Binary)
    model.Makespan = Var(within=NonNegativeReals, bounds=(0, 10000))
    model.WorkerOverlapBinary = Var(model.Processes, model.Processes, model.Workers, within=Binary)
    model.RunsDuringProduction = Var(model.Processes, within=Binary)

    ######################################################################
    ##########################Constraints#################################
    ######################################################################

    # constraints for the calculation of the endtime of the process
    def processing_time_constraint(model, pr):
        if "Production" in pr:
            return model.EndTime[pr] == model.StartTime[pr] + model.ProductionTime
        else:
            return model.EndTime[pr] == model.StartTime[pr] + sum(model.ProcessingTime[pr, w] * model.WorkerAssignment[pr, w] for w in model.Workers)
    model.ProcessingTimeConstraint = Constraint(model.Processes, rule=processing_time_constraint)

    predecessors_dict = {
        row["Process"]: row["Predecessor"]
        for product in process_data.keys()
        for row in process_data[product]
    }

    model.PredecessorConstraint = ConstraintList()
    for pr in model.Processes:
        for pred in predecessors_dict.get(pr, []):  # Falls Vorgänger existieren
            if pred in model.Processes:  # Sicherstellen, dass der Vorgänger existiert
                model.PredecessorConstraint.add(model.StartTime[pr] >= model.EndTime[pred])

    def worker_assignment_constraint(model, pr):
        return sum(model.WorkerAssignment[pr, w] for w in model.Workers) == 1
    model.WorkerAssignmentConstraint = Constraint(model.Processes, rule=worker_assignment_constraint)

    def worker_usage_constraint(model, pr):
        return model.WorkerUsage[pr] == sum(model.WorkerAssignment[pr, w] for w in model.Workers)
    model.WorkerUsageConstraint = Constraint(model.Processes, rule=worker_usage_constraint)

    BIG_M = 10000  # Eine ausreichend große Zahl

    # Constraint: Prozesse mit demselben Vorgänger dürfen nicht vom "Machine Operator + Setter" ausgeführt werden
    def no_machine_operator_setter_for_common_predecessor(model, pr):
        predecessors = model.Predecessors[pr]
        for pred in predecessors:
            successors = [p for p in model.Processes if pred in model.Predecessors[p]]
            if len(successors) > 1:
                return model.WorkerAssignment[pr, 'Machine Operator + Setter'] == 0
        return Constraint.Skip

    model.NoMachineOperatorSetterForCommonPredecessor = Constraint(model.Processes, rule=no_machine_operator_setter_for_common_predecessor)

    # Worker Non-Overlap Constraint using Disjunction
    def worker_non_overlap_disjunction(model, pr1, pr2, w):
        if pr1 == pr2 or "Production" in pr1 or "Production" in pr2:
            return Disjunction.Skip  # Ein Prozess kann nicht mit sich selbst kollidieren und Produktionsprozess wird übersprungen
        
        return [
            [model.StartTime[pr1] >= model.EndTime[pr2] - BIG_M * (1 - model.WorkerAssignment[pr1, w])],
            [model.StartTime[pr2] >= model.EndTime[pr1] - BIG_M * (1 - model.WorkerAssignment[pr2, w])]
        ]
    model.WorkerNonOverlapDisjunction = Disjunction(model.Processes, model.Processes, model.Workers, rule=worker_non_overlap_disjunction)

    internal_processes = [pr for pr in model.Processes if process_data[pr.split('_')[1]][int(pr.split('_')[0]) - 1]["External/internal process"] == "Internal"]

    # Identifiziere den Produktionsprozess
    production_process = next(pr for pr in model.Processes if process_data[pr.split('_')[1]][int(pr.split('_')[0]) - 1]["External/internal process"] == " ")

    model.NoInternalDuringProduction = ConstraintList()
    for pr in internal_processes:
        model.NoInternalDuringProduction.add(
            model.StartTime[pr] >= model.EndTime[production_process] - BIG_M * (1 - model.RunsDuringProduction[pr])
        )
        model.NoInternalDuringProduction.add(
            model.StartTime[production_process] >= model.EndTime[pr] - BIG_M * model.RunsDuringProduction[pr]
        )

    def makespan_constraint(model, pr):
        return model.Makespan >= model.EndTime[pr]
    model.MakespanConstraint = Constraint(model.Processes, rule=makespan_constraint)

    def machine_operator_setter_constraint(model, pr):
        return model.WorkerAssignment[pr, 'Machine Operator + Setter'] + model.WorkerAssignment[pr, 'Machine Operator'] + model.WorkerAssignment[pr, 'Setter'] <= 1
    model.MachineOperatorSetterConstraint = Constraint(model.Processes, rule=machine_operator_setter_constraint)

    # Objective
    def objective_rule(model):
        return model.Makespan
    model.Objective = Objective(rule=objective_rule, sense=minimize)

    # Apply the transformation to convert the disjunctions to algebraic constraints
    TransformationFactory('gdp.bigm').apply_to(model)

    # Solver
    os.environ['NEOS_EMAIL'] = st.secrets["NEOS_EMAIL"]
    solver = SolverManagerFactory('neos')
    results = solver.solve(model, opt = 'cplex', tee=True)

    # Ergebnisse anzeigen
    total_cost = 0
    gantt_data = []
    shift_plan = []
    worker_costs = {w: 0 for w in model.Workers}
    base_date = pd.Timestamp.now()
    for pr in model.Processes:
        start_time = model.StartTime[pr].value
        end_time = model.EndTime[pr].value
        for w in model.Workers:
            if model.WorkerAssignment[pr, w].value == 1:
                cost = model.Cost[pr, w]
                total_cost += cost
                worker_costs[w] += cost
                product = pr.split('_')[1]
                process_index = int(pr.split('_')[0]) - 1
                label = process_data[product][process_index]['Label']
                gantt_data.append({
                    'Task': pr,
                    'Start': (base_date + pd.Timedelta(minutes=start_time)).strftime('%H:%M'),
                    'Finish': (base_date + pd.Timedelta(minutes=end_time)).strftime('%H:%M'),
                    'Resource': w,
                    'Product': product,
                    'Label': label
                })
                shift_plan.append({
                    'Process': pr,
                    'Worker': w,
                    'Product': product,
                    'Label': label,
                    'Start': (base_date + pd.Timedelta(minutes=start_time)).strftime('%H:%M'),
                    'End': (base_date + pd.Timedelta(minutes=end_time)).strftime('%H:%M'),
                    'Cost': f"{cost} €"
                })
                # print(f"Process {pr}: Start Time = {start_time}, End Time = {end_time}, Worker: {w}, Cost: {model.Cost[pr, w]}")

    print(f"Makespan: {model.Makespan.value}")
    print(f"Total Cost: {total_cost}")

    # Farben für die Produkte festlegen
    color_map = {
        'A': 'darkred',
        'B': 'dodgerblue',
        'C': 'forestgreen'
    }

    # Gantt-Diagramm erstellen
    gantt_df = pd.DataFrame(gantt_data)
    fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Resource", color="Product", color_discrete_map=color_map, hover_data=["Label"])
    fig.update_yaxes(categoryorder="total ascending")

    # Text vertikal anzeigen
    fig.update_traces(textangle=90)

    # Grid hinzufügen
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor='LightGray'),
        yaxis=dict(showgrid=True, gridcolor='LightGray')
    )

    # Gesamtzeit und -kosten exportieren
    st.session_state["makespan"] = model.Makespan.value
    st.session_state["total_costs"] = total_cost

    # Schichtplan als Tabelle anzeigen
    shift_plan_df = pd.DataFrame(shift_plan)

    # Balkendiagramm der Gesamtkosten pro Arbeiter
    worker_costs_df['Total Cost'] = worker_costs_df['Total Cost'].astype(float)
    worker_costs_chart = px.bar(worker_costs_df, x='Worker', y='Total Cost', title='Total Costs per Worker')
    worker_costs_chart.update_layout(yaxis=dict(range=[0, worker_costs_df['Total Cost'].max() * 1.1]))

    return fig, shift_plan_df, worker_costs_df
    
