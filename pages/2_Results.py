import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    layout='wide'
)

# reset the state of the optimization
st.session_state["optimization_started"] = False

st.markdown("# Results")
# Overview
if "makespan" in st.session_state:
    st.header("Overview")
    makespan_hours = st.session_state.makespan // 60
    makespan_minutes = st.session_state.makespan % 60
    total_costs = f"{st.session_state.total_costs:.2f} €"
    st.markdown(f"<h4>The duration of the set-up processes for all products is {makespan_hours} hours and {makespan_minutes:.0f} minutes</h4>", unsafe_allow_html=True)
    st.markdown(f"<h4>The total costs of the set-up processes for all products is {total_costs}</h4>", unsafe_allow_html=True)

# Gantt-Diagram
if "fig" in st.session_state:
    st.header("Gantt-Diagram of the optimized set-up process sequence")
    fig = st.session_state["fig"]
    st.plotly_chart(fig)
else:
    st.subheader("Keine Ergebnisse vorhanden, bitte erst Optimierung starten.")

# Shift-Plan
if "shift_plan" in st.session_state:
    st.header("Shift Schedule for the set-up processes")
    shift_plan_df = st.session_state.shift_plan
    workers = shift_plan_df["Worker"].unique()
    for worker in workers:
        st.subheader(f"Shift Plan for {worker}")
        worker_shift_plan = shift_plan_df[shift_plan_df["Worker"] == worker]
        worker_shift_plan = worker_shift_plan.drop(columns=["Worker"])
        st.dataframe(worker_shift_plan, use_container_width=True, hide_index=True)

# Worker-Cost-Overview
if "worker_costs_df" in st.session_state:
    st.header("Total Costs per Worker")
    worker_costs_df = st.session_state["worker_costs_df"]
    st.dataframe(worker_costs_df, use_container_width=True)

    # Balkendiagramm der Gesamtkosten pro Arbeiter mit Matplotlib
    if "costs_fig" in st.session_state:
        st.pyplot(st.session_state["costs_fig"])
