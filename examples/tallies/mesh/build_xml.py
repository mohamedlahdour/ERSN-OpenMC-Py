from math import log10
import numpy as np
import openmc
###############################################################################
# Create materials for the problem
uo2 = openmc.Material(name='UO2 fuel at 2.4% wt enrichment')
uo2.set_density('g/cm3', 10.29769)
uo2.add_element('U', 1., enrichment=2.4)
uo2.add_element('O', 2.)
helium = openmc.Material(name='Helium for gap')
helium.set_density('g/cm3', 0.001598)
helium.add_element('He', 2.4044e-4)
zircaloy = openmc.Material(name='Zircaloy 4')
zircaloy.set_density('g/cm3', 6.55)
zircaloy.add_element('Sn', 0.014  , 'wo')
zircaloy.add_element('Fe', 0.00165, 'wo')
zircaloy.add_element('Cr', 0.001  , 'wo')
zircaloy.add_element('Zr', 0.98335, 'wo')
borated_water = openmc.Material(name='Borated water')
borated_water.set_density('g/cm3', 0.740582)
borated_water.add_element('B', 4.0e-5)
borated_water.add_element('H', 5.0e-2)
borated_water.add_element('O', 2.4e-2)
borated_water.add_s_alpha_beta('c_H_in_H2O')
uranium1 = openmc.Material(name='uranium1', temperature=293.6)
uranium1.set_density('g/cm3', 19)
uranium1.add_nuclide('U235', 1, percent_type='wo')
# Collect the materials together and export to XML
materials = openmc.Materials([uo2, helium, zircaloy, borated_water, uranium1])
materials.export_to_xml()
###############################################################################
# Define problem geometry
# Create cylindrical surfaces
fuel_or = openmc.ZCylinder(r=2.39218, name='Fuel OR')
clad_ir = openmc.ZCylinder(r=2.40005, name='Clad IR')
clad_or = openmc.ZCylinder(r=2.45720, name='Clad OR')
Surf4= openmc.Sphere(surface_id=4, x0=-3, y0=-3, z0=0.0, r=1.0, name='Surf4')
# Create a region represented as the inside of a rectangular prism
pitch = 10.25984
box = openmc.rectangular_prism(pitch, pitch, boundary_type='reflective')
# Create cells, mapping materials to regions
fuel = openmc.Cell(fill=uo2, region=-fuel_or)
gap = openmc.Cell(fill=helium, region=+fuel_or & -clad_ir)
clad = openmc.Cell(fill=zircaloy, region=+clad_ir &  -clad_or)
water = openmc.Cell(fill=borated_water, region=+clad_or & +Surf4 & box)
# Create a geometry and export to XML
Cell6= openmc.Cell(cell_id=6, name='Cell6')
Cell6.region = -Surf4
Cell6.fill = uranium1
geometry = openmc.Geometry([fuel, gap, clad, water, Cell6])
geometry.export_to_xml() 
###############################################################################
# Define problem settings
# Indicate how many particles to run
settings = openmc.Settings()
settings.batches = 1100
settings.inactive = 100
settings.particles = 10000
# Create an initial uniform spatial source distribution over fissionable zones
lower_left = (-pitch/2, -pitch/2, -1)
upper_right = (pitch/2, pitch/2, 1)
uniform_dist = openmc.stats.Box(lower_left, upper_right, only_fissionable=True)
settings.source = openmc.source.Source(space=uniform_dist)
# For source convergence checks, add a mesh that can be used to calculate the
# Shannon entropy
# entropy_mesh = openmc.RegularMesh()
# entropy_mesh.lower_left = (-fuel_or.r, -fuel_or.r)
# entropy_mesh.upper_right = (fuel_or.r, fuel_or.r)
# entropy_mesh.dimension = (10, 10)
# settings.entropy_mesh = entropy_mesh
settings.export_to_xml()
###############################################################################
# Define tallies
# Create a mesh that will be used for tallying
mesh = openmc.RegularMesh()
mesh.dimension = (36, 36, 36)
mesh.lower_left = (-pitch/2, -pitch/2, -5)
mesh.upper_right = (pitch/2, pitch/2, 5)
# Create a mesh filter that can be used in a tally
mesh_filter = openmc.MeshFilter(mesh)
# Now use the mesh filter in a tally and indicate what scores are desired
# Let's also create a tally to get the flux energy spectrum. We start by
# creating an energy filter
e_min, e_max = 1e-5, 20.0e6
groups = 50
energies = np.logspace(log10(e_min), log10(e_max), groups + 1)
energy_filter = openmc.EnergyFilter(energies)
energy_filter1 = openmc.EnergyFilter([1E-5, 0.625, 2E7])
cell_filter = openmc.CellFilter([fuel, gap, clad, water])
# Instantiate a Tallies collection and export to XML
tallies = openmc.Tallies()
_tally1 = openmc.Tally(tally_id=1, name='RR5')
_tally1.filters += [mesh_filter]
_tally1.scores = ['absorption', 'fission', 'flux']
tallies.append(_tally1)
_tally2 = openmc.Tally(tally_id=2, name='RR5')
_tally2.filters += [mesh_filter]
_tally2.nuclides = ['Fe57', 'U235', 'Zr90']
_tally2.scores = ['absorption', 'fission', 'elastic']
tallies.append(_tally2)
_tally5 = openmc.Tally(tally_id=5, name='RR5')
_tally5.filters += [mesh_filter, cell_filter]
_tally5.nuclides = ['Fe57', 'Fe54', 'Zr90']
_tally5.scores = ['absorption', 'fission']
tallies.append(_tally5)
mesh3 = openmc.RegularMesh(mesh_id=3)
mesh3.dimension = [60, 60]
mesh3.lower_left = [-10.1, -10.1]
mesh3.upper_right = [10.1, 10.1]
Mesh_filter6 = openmc.MeshFilter(mesh3, filter_id=6)
mesh4 = openmc.RegularMesh(mesh_id=4)
mesh4.dimension = [30, 30, 15]
mesh4.lower_left = [-10.1, -10.1, -5.0]
mesh4.upper_right = [10.1, 10.1, 5.0]
Mesh_filter7 = openmc.MeshFilter(mesh4, filter_id=7)
_tally7 = openmc.Tally(tally_id=7, name='mesh_energy')
_tally7.filters += [Mesh_filter7, energy_filter1]
_tally7.nuclides = ['U235', 'Zr90']
_tally7.scores = ['absorption', 'elastic', 'fission', 'total']
tallies.append(_tally7)
_tally8 = openmc.Tally(tally_id=8, name='mesh_nuclides')
_tally8.filters += [Mesh_filter7]
_tally8.nuclides = ['U235', 'Zr90', 'B10']
_tally8.scores = ['absorption', 'elastic', '(n,gamma)', 'total']
tallies.append(_tally8)
_tally9 = openmc.Tally(tally_id=9, name='mesh_energy_nuclides')
_tally9.filters += [Mesh_filter6, energy_filter1]
_tally9.scores = ['absorption', 'elastic', '(n,gamma)', 'total']
tallies.append(_tally9)
_tally10 = openmc.Tally(tally_id=10, name='mesh 2D')
_tally10.filters += [Mesh_filter6]
_tally10.scores = ['absorption', 'elastic', '(n,gamma)', 'total']
tallies.append(_tally10)
mesh_tally = openmc.Tally(name='Mesh tally')
mesh_tally.filters = [mesh_filter]
mesh_tally.scores = ['flux', 'fission', 'nu-fission']
tallies.append(mesh_tally)
tallies.export_to_xml()
############################################################################### 
#                 Exporting to OpenMC geometry.xml file                        
###############################################################################
############################################################################### 
#                 Exporting to OpenMC plots.xml file                        
###############################################################################
_plot1 = openmc.Plot(plot_id= 1 )
_plot1.filename = '_plot1'
_plot1.origin = (0,0,0)
_plot1.width = (12,12)
_plot1.pixels = (500,500)
_plot1.color_by = 'material'
_plot1.basis = 'xy'
_plot2 = openmc.Plot(plot_id= 2 )
_plot2.filename = '_plot2'
_plot2.origin = (0,0,0)
_plot2.width = (12,12,12)
_plot2.pixels = (100,100,100)
_plot2.type ="voxel"
_plot2.color_by = 'material'
plots = openmc.Plots( [_plot1, _plot2] )
plots.export_to_xml()
openmc.run()