
import os  # using operating system-dependent functionality
from pathlib import Path # provides an object-oriented interface for working with file paths
import random # random number generators for various distributions

from compas.datastructures import Mesh  # used for computational geometry, not as same as the mesh in FEM

import compas_fea2
from compas_fea2.model import Model, DeformablePart, Node # Model Components
from compas_fea2.model import RectangularSection, ElasticIsotropic, ShellSection # Material and Section Properties
from compas_fea2.model import BeamElement
from compas_fea2.problem import Problem, StaticStep, FieldOutput, LoadCombination # Problem Definition and Analysis
from compas_fea2.units import units #  imports the units function from the compas_fea2.units
units = units(system='SI_mm') # set the metric system with millimeters as the unit of length

# compas_fea2.set_backend('compas_fea2_sofistik')
# compas_fea2.set_backend('compas_fea2_opensees')
compas_fea2.set_backend('compas_fea2_abaqus') # all subsequent analysis tasks are carried out using Abaqus

HERE = os.path.dirname(__file__) # "HERE" will hold the directory path where the current script is located

mdl = Model(name='simple_frame') # creates an instance of the Model class from the compas_fea2 library 
nodes = [
    Node(xyz=(0, 0, 0)),
    Node(xyz=(100, 0, 0)),
    Node(xyz=(200, 0, 0)),
    Node(xyz=(500, 0, 0)),
    Node(xyz=(0, 100, 0)),
    Node(xyz=(100, 100,0)),
    Node(xyz=(200, 100, 0)),
    Node(xyz=(500, 100, 0)),
    Node(xyz=(0, 110, 0)),
    Node(xyz=(100, 110,0)),
    Node(xyz=(200, 110,0)),
    Node(xyz=(500, 110, 0)),  
]

# Create deformable part from the nodes and elements
prt = DeformablePart(name='frame_part')

# Add nodes to the model
prt.add_nodes(nodes)

# Define material in the same unit system
mat = ElasticIsotropic(E=210*units.GPa, 
                       v=0.2, 
                       density=7800*units("kg/m**3"))

# Define section
sec = RectangularSection(w=10*units.cm, h=200*units.mm, material=mat)

## no model.add_section(section)?

# Create elements (beams) to connect the nodes
for c, _ in enumerate(nodes):
    if c == len(nodes)-1:
        break
    prt.add_element(BeamElement(nodes=[nodes[c], nodes[c+1]], section=sec))

mdl.add_part(prt)

# Add boundary conditions 
#fix the left bottom node
mdl.add_pin_bc(nodes=prt.find_nodes_around_point([0, 0, 0], distance=0.1))
mdl.add_rollerX_bc(nodes=prt.find_nodes_around_point([500, 0, 0], distance=0.1))

mdl.summary() # Summarizes the model setup.

# DEFINE THE PROBLEM
prb = Problem()
# define a step
step_1 = StaticStep()
step_1.combination = LoadCombination.ULS()

# Apply load to a on Node(x=200, y=110, z=0)
load_node = prt.find_nodes_around_point((200, 110, 0), distance=0.1)
step_1.add_node_pattern(nodes=[load_node], y=-10 * units.kN, load_case='LL')

# Define field outputs
fout = FieldOutput(node_outputs=['U', 'RF'],
                   element_outputs=['SF'])
step_1.add_output(fout)
# hout = HistoryOutput('hout_test')

# set-up the problem
prb = Problem('00_simple_problem')
prb.add_step(step_1)
prb.summary()  # Summarizes the problem setup.


mdl.add_problem(problem=prb)
# mdl.analyse_and_extract(problems=[prb], path=HERE, verbose=True)
# prb.show_deformed(scale_factor=1000, draw_loads=0.1, draw_bcs=0.25)

# mdl.to_cfm(DATA+'\simple_frame.cfm')