import graphviz as gv
import pandas as pd
import plotly.graph_objects as go

# function that takes a dataframe as input and returns a graphviz graph object
def create_graph(df):
    graph = gv.Digraph()
    graph.attr(rankdir='LR')  # Set the direction of the graph

    # Add a subgraph for the legend
    with graph.subgraph(name='cluster_legend') as legend:
        legend.attr(label='Legend', fontsize='12')  # Set the fontsize to a smaller value
        legend.node('Internal', label='Internal Process', style='filled', fillcolor='firebrick3', shape='rect', penwidth='1', color='black')
        legend.node('External', label='External Process', style='filled', fillcolor='gray47', shape='rect', penwidth='1', color='black')
        legend.node('Other', label='Production Process', style='filled', fillcolor='green', shape='rect', penwidth='1', color='black')
        legend.attr(rank='same')
        legend.edge('Internal', 'External', style='invis')
        legend.edge('External', 'Other', style='invis')

    # Create a dictionary to store nodes by their level
    levels = {}
    for index, row in df.iterrows():
        for predecessor in row['Predecessor']:
            if predecessor not in levels:
                levels[predecessor] = []
            levels[predecessor].append(row['Process'])

    # Add nodes to the graph
    for index, row in df.iterrows():
        if row['External/internal process'] == 'Internal':
            fillcolor = 'firebrick3'
        elif row['External/internal process'] == 'External':
            fillcolor = 'gray47'
        else:
            fillcolor = 'green'
        
        # Customize the node label with only the process number
        label = f"{row['Process']}"
        graph.node(str(row['Process']), label=label, style='filled', fillcolor=fillcolor, shape='rect', penwidth='1', color='black')

    # Add edges to the graph
    for index, row in df.iterrows():
        for predecessor in row['Predecessor']:
            if predecessor != 0:
                graph.edge(str(predecessor), str(row['Process']))

    # Add subgraphs for vertical lines
    for level, nodes in levels.items():
        if len(nodes) > 1:
            with graph.subgraph() as s:
                s.attr(rank='same')
                for node in nodes:
                    s.node(str(node))
                # Add invisible nodes and edges to create vertical lines
                for i in range(len(nodes) - 1):
                    invisible_node = f"invis_{level}_{i}"
                    s.node(invisible_node, style='invis')
                    s.edge(str(nodes[i]), invisible_node, style='invis')
                    s.edge(invisible_node, str(nodes[i + 1]), style='invis')

    return graph
