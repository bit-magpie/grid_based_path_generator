
# Import Grid class
from grid_generator import Grid

# Create an instance of Grid class by feeding PGM file path and YAML file path
grid = Grid('map.pgm', 'map.yaml')

# Run build_graph() function to get visibility graph
# Visibility graph is a dictionary of tuples 
# For example {(x0,y0): [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]}
graph_meter, graph_pixel = grid.build_graph()

#------------------------ Optional ---------------------------
import numpy as np
import matplotlib.pyplot as plt

# Plotting visibility graph of relative coordinates
cords = list()
for key in graph_meter:
    for vertex in graph_meter[key]:
        l = np.array([key, vertex])
        xs, ys = zip(*l)
        plt.plot(xs,ys)

plt.show()