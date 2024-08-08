
import os  # using operating system-dependent functionality
from pathlib import Path # provides an object-oriented interface for working with file paths
import random # random number generators for various distributions

from compas.datastructures import Mesh  # used for computational geometry, not as same as the mesh in FEM

import compas_fea2
from compas_fea2.model import Model, DeformablePart, Node # Model Components
from compas_fea2.model import RectangularSection, ElasticIsotropic, ShellSection # Material and Section Properties
from compas_fea2.problem import Problem, StaticStep, FieldOutput, LoadCombination # Problem Definition and Analysis
from compas_fea2.units import units #  imports the units function from the compas_fea2.units
units = units(system='SI_mm') # set the metric system with millimeters as the unit of length

# compas_fea2.set_backend('compas_fea2_sofistik')
# compas_fea2.set_backend('compas_fea2_opensees')
compas_fea2.set_backend('compas_fea2_abaqus') # all subsequent analysis tasks are carried out using Abaqus
# compas_fea2.set_backend('abaqus')

HERE = os.path.dirname(__file__) # "HERE" will hold the directory path where the current script is located

mdl = Model(name='simple_frame') # creates an instance of the Model class from the compas_fea2 library 
# Define nodes in millimeters
nodes = [
    # nodes bottom row
    Node(x=0, y=0, z=0),
    Node(x=100, y=0, z=0),
    Node(x=200, y=0, z=0),
    Node(x=500, y=0, z=0),
    # nodes middle row
    Node(x=0, y=100, z=0),
    Node(x=100, y=100, z=0),
    Node(x=200, y=100, z=0),
    Node(x=500, y=100, z=0),    
    # nodes top row
    Node(x=0, y=110, z=0),
    Node(x=100, y=110, z=0),
    Node(x=200, y=110, z=0),
    Node(x=500, y=110, z=0)   
]

# Add nodes to the model
for node in nodes:
    model.add_node(node)

# Define material in the same unit system
mat = ElasticIsotropic(E=210*units.GPa, 
                       v=0.2, 
                       density=7800*units("kg/m**3"))

# Define section
sec = RectangularSection(w=100, h=200, material=mat)
## no model.add_section(section)?

# Create elements (beams) to connect the nodes
elements = [
    BeamElement(sec, nodes[0], nodes[1]),
    BeamElement(sec, nodes[1], nodes[2]),
    BeamElement(sec, nodes[2], nodes[3]),
    BeamElement(sec, nodes[4], nodes[5]),
    BeamElement(sec, nodes[5], nodes[6]),
    BeamElement(sec, nodes[6], nodes[7]),
    BeamElement(sec, nodes[8], nodes[9]),
    BeamElement(sec, nodes[9], nodes[10]),
    BeamElement(sec, nodes[10], nodes[11]),
    BeamElement(sec, nodes[0], nodes[4]),
    BeamElement(sec, nodes[1], nodes[5]),
    BeamElement(sec, nodes[2], nodes[6]),
    BeamElement(sec, nodes[3], nodes[7]),
    BeamElement(sec, nodes[4], nodes[8]),
    BeamElement(sec, nodes[5], nodes[9]),
    BeamElement(sec, nodes[6], nodes[10]),
    BeamElement(sec, nodes[7], nodes[11])
]

# Create deformable part from the nodes and elements
prt = DeformablePart(name='frame_part')
for node in nodes:
    prt.add_node(node)
for element in elements:
    prt.add_element(element)

mdl.add_part(prt)

# Add boundary conditions 
#fix the left bottom node
fixed_nodes1 = fixed_nodes = [prt.find_node_by_coordinates(0, 0, 0)]
mdl.add_fix_bc(nodes=fixed_nodes)
# fix the right bottom node
fixed_nodes2 = fixed_nodes = [prt.find_node_by_coordinates(, 0, 0)]
mdl.add_fix_bc(nodes=fixed_nodes)
mdl.summary() # Summarizes the model setup.

# DEFINE THE PROBLEM
# define a step
step_1 = StaticStep()
step_1.combination = LoadCombination.ULS()

# Apply load to a on Node(x=200, y=110, z=0)
load_node = prt.find_node_by_coordinates(200, 110, 0)
step_1.add_node_pattern(nodes=[load_node], y=-10 * units.kN, load_case='LL')

# Define field outputs
fout = FieldOutput(node_outputs=['U', 'RF'],
                   element_outputs=['SF'])
step_1.add_output(fout)
# hout = HistoryOutput('hout_test')

# set-up the problem
prb = Problem('00_simple_problem', mdl)
prb.add_step(step_1)
prb.summary()  # Summarizes the problem setup.

# mdl.add_problem(problem=prb)
# mdl.analyse_and_extract(problems=[prb], path=TEMP, verbose=True)
# prb.show_deformed(scale_factor=1000, draw_loads=0.1, draw_bcs=0.25)

# mdl.to_cfm(DATA+'\simple_frame.cfm')