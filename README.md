# Lego-Baustein-Ruestungszeit-Optimierungs-Software-Dingsbums (LBROSD) 
Im Rahmen des Moduls "Discrete-event Simulation and Organization Methods" ist diese Software zur Optimierung der zeitlichen Organisation von Ruestprozessen entstanden. Diese Seite dient als Dokumentation dieser Software. Ab hier dann auf Englisch.

## Software Description

The **LBROSR** is a software for optimizing the sequence of set-up processes for one machine and constraint worker-resources. The goal is to find the set-up-process-schedule with the lowest time. The machine can produce three types of Lego-Bricks and each Brick or Product has its own unique set-up process. The software consists of three pages: This page, an **Initialisation** Page and a **Results** Page. On the Page **Initialisation**, you can visualize the process-data and choose the production order of the three different bricks. On the **Results**-Page there are different graphs and tables of the calculated results.

The software is completely written in Python and uses the package **Pyomo** for the optimization. The website is programmed with **Streamlit**. 

#### Contact information 
Julius Berghoff  
Sebastian Heise  
Laura Driftmeyer  
