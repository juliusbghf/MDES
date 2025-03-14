import pandas as pd
import streamlit as st
import graphviz as gv
from streamlit.components.v1 import html
from graph_functions import create_graph
from optimization import start_optimization

st.set_page_config(
    layout='wide'
)


def nav_page(page_name, timeout_secs=3) -> None:
    """
        Javascript used to switch between to Streamlit pages
        automatically.

        :param page_name: string containing the pages name possible \
            entries are: Result_Processing, Urban_District_Upscaling, ...
        :type page_name: str
        :param timeout_secs: seconds until system returns timeout
        :type timeout_secs: float
    """
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/"
                        + page_name.toLowerCase())) {
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name,
                               start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name
                          + "' after " + timeout_secs + " second(s).");
                }
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d);
            });
        </script>
    """ % (page_name, timeout_secs)
    html(nav_script)

# create the dataframes for the processes (Product A and B)
product_A = pd.DataFrame([
    {"Process": "1_A", "Label": "Clean tool", "Predecessor": [], "Processing Time Machine Operator": 70, "Cost Machine Operator": 28, "Processing Time Setter": 40, "Cost Setter": 24, "Processing Time Machine Operator + Setter": 20, "Cost Machine Operator + Setter": 30, "External/internal process": "External"},
    {"Process": "2_A", "Label": "Transport the tool", "Predecessor": ["1_A"], "Processing Time Machine Operator": 5, "Cost Machine Operator": 2, "Processing Time Setter": 5, "Cost Setter": 3, "Processing Time Machine Operator + Setter": 5, "Cost Machine Operator + Setter": 5, "External/internal process": "External"},
    {"Process": "3_A", "Label": "Mount tool on IMM", "Predecessor": ["2_A"], "Processing Time Machine Operator": 20, "Cost Machine Operator": 8, "Processing Time Setter": 15, "Cost Setter": 9, "Processing Time Machine Operator + Setter": 10, "Cost Machine Operator + Setter": 10, "External/internal process": "Internal"},
    {"Process": "4_A", "Label": "Connect cooling water to tool", "Predecessor": ["2_A"], "Processing Time Machine Operator": 12, "Cost Machine Operator": 4.8, "Processing Time Setter": 8, "Cost Setter": 4.8, "Processing Time Machine Operator + Setter": 6, "Cost Machine Operator + Setter": 6, "External/internal process": "Internal"},
    {"Process": "5_A", "Label": "Heat up the tool", "Predecessor": ["3_A", "4_A"], "Processing Time Machine Operator": 30, "Cost Machine Operator": 12, "Processing Time Setter": 30, "Cost Setter": 12, "Processing Time Machine Operator + Setter": 30, "Cost Machine Operator + Setter": 30, "External/internal process": "Internal"},
    {"Process": "6_A", "Label": "Production", "Predecessor": ["5_A"], "Processing Time Machine Operator": 60, "Cost Machine Operator": 0, "Processing Time Setter": 60, "Cost Setter": 0, "Processing Time Machine Operator + Setter": 60, "Cost Machine Operator + Setter": 0, "External/internal process": " "},
    {"Process": "7_A", "Label": "Empty injection unit", "Predecessor": ["6_A"], "Processing Time Machine Operator": 4, "Cost Machine Operator": 1.6, "Processing Time Setter": 2, "Cost Setter": 1.2, "Processing Time Machine Operator + Setter": 1, "Cost Machine Operator + Setter": 1, "External/internal process": "Internal"},
    {"Process": "8_A", "Label": "Switch off heating", "Predecessor": ["7_A"], "Processing Time Machine Operator": 2, "Cost Machine Operator": 0.8, "Processing Time Setter": 2, "Cost Setter": 1.2, "Processing Time Machine Operator + Setter": 2, "Cost Machine Operator + Setter": 2, "External/internal process": "Internal"},
    {"Process": "9_A", "Label": "Empty granulate storage", "Predecessor": ["7_A"], "Processing Time Machine Operator": 3, "Cost Machine Operator": 1.2, "Processing Time Setter": 3, "Cost Setter": 1.8, "Processing Time Machine Operator + Setter": 2, "Cost Machine Operator + Setter": 2, "External/internal process": "Internal"},
    {"Process": "10_A", "Label": "Switch off tool tempering", "Predecessor": ["7_A"], "Processing Time Machine Operator": 10, "Cost Machine Operator": 4, "Processing Time Setter": 6, "Cost Setter": 4, "Processing Time Machine Operator + Setter": 4, "Cost Machine Operator + Setter": 4, "External/internal process": "Internal"},
    {"Process": "11_A", "Label": "Dismantle tool", "Predecessor": ["8_A", "9_A", "10_A"], "Processing Time Machine Operator": 16, "Cost Machine Operator": 6.4, "Processing Time Setter": 12, "Cost Setter": 7.2, "Processing Time Machine Operator + Setter": 5, "Cost Machine Operator + Setter": 5, "External/internal process": "Internal"}
])

product_B = pd.DataFrame([
    {"Process": "1_B", "Label": "Check tool", "Predecessor": [], "Processing Time Machine Operator": 20, "Cost Machine Operator": 8, "Processing Time Setter": 10, "Cost Setter": 6, "Processing Time Machine Operator + Setter": 8, "Cost Machine Operator + Setter": 8, "External/internal process": "External"},
    {"Process": "2_B", "Label": "Mount tool on IMM", "Predecessor": ["1_B"], "Processing Time Machine Operator": 20, "Cost Machine Operator": 8, "Processing Time Setter": 15, "Cost Setter": 9, "Processing Time Machine Operator + Setter": 10, "Cost Machine Operator + Setter": 10, "External/internal process": "External"},
    {"Process": "3_B", "Label": "Heat up IMM", "Predecessor": ["2_B"], "Processing Time Machine Operator": 5, "Cost Machine Operator": 2, "Processing Time Setter": 5, "Cost Setter": 3, "Processing Time Machine Operator + Setter": 5, "Cost Machine Operator + Setter": 5, "External/internal process": "Internal"},
    {"Process": "4_B", "Label": "Fill up IMM with granulate", "Predecessor": ["3_B"], "Processing Time Machine Operator": 3, "Cost Machine Operator": 1.2, "Processing Time Setter": 2, "Cost Setter": 1.2, "Processing Time Machine Operator + Setter": 1, "Cost Machine Operator + Setter": 1, "External/internal process": "Internal"},
    {"Process": "5_B", "Label": "Approach tool", "Predecessor": ["4_B"], "Processing Time Machine Operator": 10, "Cost Machine Operator": 4, "Processing Time Setter": 5, "Cost Setter": 3, "Processing Time Machine Operator + Setter": 7, "Cost Machine Operator + Setter": 7, "External/internal process": "Internal"},
    {"Process": "6_B", "Label": "Production", "Predecessor": ["5_B"], "Processing Time Machine Operator": 60, "Cost Machine Operator": 0, "Processing Time Setter": 60, "Cost Setter": 0, "Processing Time Machine Operator + Setter": 60, "Cost Machine Operator + Setter": 0, "External/internal process": " "},
    {"Process": "7_B", "Label": "Empty injection unit", "Predecessor": ["6_B"], "Processing Time Machine Operator": 4, "Cost Machine Operator": 1.6, "Processing Time Setter": 2, "Cost Setter": 1.2, "Processing Time Machine Operator + Setter": 1, "Cost Machine Operator + Setter": 1, "External/internal process": "Internal"},
    {"Process": "8_B", "Label": "Switch off heating", "Predecessor": ["7_B"], "Processing Time Machine Operator": 2, "Cost Machine Operator": 0.8, "Processing Time Setter": 2, "Cost Setter": 1.2, "Processing Time Machine Operator + Setter": 2, "Cost Machine Operator + Setter": 2, "External/internal process": "Internal"},
    {"Process": "9_B", "Label": "Empty granulate storage", "Predecessor": ["7_B"], "Processing Time Machine Operator": 3, "Cost Machine Operator": 1.2, "Processing Time Setter": 3, "Cost Setter": 1.8, "Processing Time Machine Operator + Setter": 2, "Cost Machine Operator + Setter": 2, "External/internal process": "Internal"},
    {"Process": "10_B", "Label": "Switch off tool tempering", "Predecessor": ["7_B"], "Processing Time Machine Operator": 10, "Cost Machine Operator": 4, "Processing Time Setter": 6, "Cost Setter": 4, "Processing Time Machine Operator + Setter": 4, "Cost Machine Operator + Setter": 4, "External/internal process": "Internal"},
    {"Process": "11_B", "Label": "Dismantle tool", "Predecessor": ["8_B", "9_B", "10_B"], "Processing Time Machine Operator": 16, "Cost Machine Operator": 6.4, "Processing Time Setter": 12, "Cost Setter": 7.2, "Processing Time Machine Operator + Setter": 5, "Cost Machine Operator + Setter": 5, "External/internal process": "Internal"}
])

product_C = pd.DataFrame([
    {"Process": "1_C", "Label": "Mount tool on IMM", "Predecessor": [], "Processing Time Machine Operator": 20, "Cost Machine Operator": 8, "Processing Time Setter": 15, "Cost Setter": 9, "Processing Time Machine Operator + Setter": 10, "Cost Machine Operator + Setter": 10, "External/internal process": "External"},
    {"Process": "2_C", "Label": "Heat up injection unit", "Predecessor": ["1_C"], "Processing Time Machine Operator": 20, "Cost Machine Operator": 8, "Processing Time Setter": 20, "Cost Setter": 12, "Processing Time Machine Operator + Setter": 20, "Cost Machine Operator + Setter": 20, "External/internal process": "External"},
    {"Process": "3_C", "Label": "Empty injection unit", "Predecessor": ["2_C"], "Processing Time Machine Operator": 4, "Cost Machine Operator": 1.6, "Processing Time Setter": 2, "Cost Setter": 1.2, "Processing Time Machine Operator + Setter": 1, "Cost Machine Operator + Setter": 1, "External/internal process": "Internal"},
    {"Process": "4_C", "Label": "Change injection unit", "Predecessor": ["3_C"], "Processing Time Machine Operator": 30, "Cost Machine Operator": 12, "Processing Time Setter": 20, "Cost Setter": 12, "Processing Time Machine Operator + Setter": 10, "Cost Machine Operator + Setter": 10, "External/internal process": "Internal"},
    {"Process": "5_C", "Label": "Fill up IMM with granulate", "Predecessor": ["4_C"], "Processing Time Machine Operator": 3, "Cost Machine Operator": 1.2, "Processing Time Setter": 2, "Cost Setter": 1.2, "Processing Time Machine Operator + Setter": 1, "Cost Machine Operator + Setter": 1, "External/internal process": "Internal"},
    {"Process": "6_C", "Label": "Production", "Predecessor": ["5_C"], "Processing Time Machine Operator": 60, "Cost Machine Operator": 0, "Processing Time Setter": 60, "Cost Setter": 0, "Processing Time Machine Operator + Setter": 60, "Cost Machine Operator + Setter": 0, "External/internal process": " "},
    {"Process": "7_C", "Label": "Empty injection unit", "Predecessor": ["6_C"], "Processing Time Machine Operator": 4, "Cost Machine Operator": 1.6, "Processing Time Setter": 2, "Cost Setter": 1.2, "Processing Time Machine Operator + Setter": 1, "Cost Machine Operator + Setter": 1, "External/internal process": "Internal"},
    {"Process": "8_C", "Label": "Switch off heating", "Predecessor": ["7_C"], "Processing Time Machine Operator": 2, "Cost Machine Operator": 0.8, "Processing Time Setter": 2, "Cost Setter": 1.2, "Processing Time Machine Operator + Setter": 2, "Cost Machine Operator + Setter": 2, "External/internal process": "Internal"},
    {"Process": "9_C", "Label": "Empty granulate storage", "Predecessor": ["7_C"], "Processing Time Machine Operator": 3, "Cost Machine Operator": 1.2, "Processing Time Setter": 3, "Cost Setter": 1.8, "Processing Time Machine Operator + Setter": 2, "Cost Machine Operator + Setter": 2, "External/internal process": "Internal"},
    {"Process": "10_C", "Label": "Switch off tool tempering", "Predecessor": ["7_C"], "Processing Time Machine Operator": 10, "Cost Machine Operator": 4, "Processing Time Setter": 6, "Cost Setter": 4, "Processing Time Machine Operator + Setter": 4, "Cost Machine Operator + Setter": 4, "External/internal process": "Internal"},
    {"Process": "11_C", "Label": "Dismantle tool", "Predecessor": ["8_C", "9_C", "10_C"], "Processing Time Machine Operator": 16, "Cost Machine Operator": 6.4, "Processing Time Setter": 12, "Cost Setter": 7.2, "Processing Time Machine Operator + Setter": 5, "Cost Machine Operator + Setter": 5, "External/internal process": "Internal"}
])


st.markdown("# Initialisation")
st.markdown("* On this page, you can visualize and initialize the data. There are three products with different sequences of setup-processes that are fixed. At first you have the option to visualize the set-up processes of each product. For each product there is a tabular and graphical representation.")
st.markdown("* In total the workforce for fulfilling the processes consists of two workers, a machine operator and a setter, that can either fulfill these tasks alone or together. For each of these options there is a processing time and a related cost.")
st.markdown("* The processes can either be internal, meaning from 'inside' of the machine, or external, meaning from 'outside' of the machine. Also included is a production process.")
st.markdown("* The graphical visualisation shows the sequence of processes with the predecessor relationships.")
# check if the session state for the visualisation is set
if "visualisation" not in st.session_state:
    st.session_state.visualisation = "Product A"
    st.session_state.df_visualisation = product_A

st.header("Set-up processes of the products")
# st.session_state.visualisation = st.select_slider("Select the product to visualize", options=["Product A", "Product B", "Product C"], key = "product_slider")
st.session_state.visualisation = st.radio("Select the product to visualize", ["Product A", "Product B", "Product C"], captions=["Roter 4x4 Stein", "Blauer 2x1 Stein", "Grüner 6x2 Stein"])
st.subheader("Tabular representation of the set-up processes for " + st.session_state.visualisation)
# display the dataframe and the graph of the selected product
if st.session_state.visualisation == "Product A":
    st.session_state.df_visualisation = product_A
    st.dataframe(st.session_state.df_visualisation, hide_index = True)
    graph = create_graph(product_A)
    st.session_state.product_graph = graph
    st.subheader("Graphical representation of the set-up processes for " + st.session_state.visualisation)
    st.graphviz_chart(st.session_state.product_graph, use_container_width=True,)

elif st.session_state.visualisation == "Product B":
    st.session_state.df_visualisation = product_B
    st.dataframe(st.session_state.df_visualisation, hide_index = True)
    graph = create_graph(product_B)
    st.session_state.product_graph = graph
    st.subheader("Graphical representation of the set-up processes for " + st.session_state.visualisation)
    st.graphviz_chart(st.session_state.product_graph, use_container_width=True)

elif st.session_state.visualisation == "Product C":
    st.session_state.df_visualisation = product_C
    st.dataframe(st.session_state.df_visualisation, hide_index = True)
    graph = create_graph(product_C)
    st.session_state.product_graph = graph
    st.subheader("Graphical representation of the set-up processes for " + st.session_state.visualisation)
    st.graphviz_chart(st.session_state.product_graph, use_container_width=True)

# select the order of the products for the machine
order_df = pd.DataFrame([
    {"Product A": 1, "Product B": 2, "Product C": 3}
])
st.header("Select the order of the products for the machine:")
st.markdown("* After visualising the data you can decide in which order the products should be produced. By double-clicking the number a drop-down menu will open, in which you can use a number for each product. Number 1 will be produced first, number 2 second and number 3 third. Please choose each number only once, else the optimization will not work! ")
st.session_state.order_df = st.data_editor(order_df, 
                            use_container_width=True, 
                            hide_index = True,
                            column_config={
                                    "Product A": st.column_config.SelectboxColumn(options=[1, 2, 3]),
                                    "Product B": st.column_config.SelectboxColumn(options=[1, 2, 3]),
                                    "Product C": st.column_config.SelectboxColumn(options=[1, 2, 3])
                            })

# boolean to check if the data for the products has been submitted or not
if "optimization_started" not in st.session_state:
    st.session_state["optimization_started"] = False

def handle_state_optimization_started() -> None:
    st.session_state["optimization_started"] = True
    st.session_state["submit_clicked"] = True

st.header("Submit data and start optimization")
# submit button for starting the optimization
with st.form(key="submit_data"):
    st.write("Press the button to submit the created data and start the optimization.")
    submit = st.form_submit_button(
                label = "Submit data",
                on_click = handle_state_optimization_started
            )
    
if st.session_state["optimization_started"] == True:
    # Create three dataframes for Product 1, Product 2, and Product 3
    product_1 = pd.DataFrame()
    product_2 = pd.DataFrame()
    product_3 = pd.DataFrame()

    # Assign products to the created dataframes according to the order_df
    order = st.session_state.order_df.iloc[0]

    if order["Product A"] == 1:
        product_1 = product_A
    elif order["Product A"] == 2:
        product_2 = product_A
    elif order["Product A"] == 3:
        product_3 = product_A

    if order["Product B"] == 1:
        product_1 = product_B
    elif order["Product B"] == 2:
        product_2 = product_B
    elif order["Product B"] == 3:
        product_3 = product_B

    if order["Product C"] == 1:
        product_1 = product_C
    elif order["Product C"] == 2:
        product_2 = product_C
    elif order["Product C"] == 3:
        product_3 = product_C

    # create spinner info text
    st.info("Optimization started. Please wait until the optimization is finished.", icon = "ℹ️")
    
    # start the optimization
    st.session_state["fig"], st.session_state["shift_plan"], st.session_state["worker_costs_df"] = start_optimization(product_1, product_2, product_3)

    # change the page to the results page
    nav_page("Results", timeout_secs=2)
