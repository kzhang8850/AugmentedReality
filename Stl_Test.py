import numpy
from stl import mesh
your_mesh = mesh.Mesh.from_file('Triangle_Cad.STL')

print your_mesh[3]