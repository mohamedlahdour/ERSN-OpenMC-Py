import numpy as np
#! /usr/bin/python3 
#! -*- coding:utf-8 -*- 
import openmc
''' 
 ==========================================================================
 Description: test
 Case: 04
 Writen by: TB
 DateTime: 13/05/2022 15:32:04
 ==========================================================================
'''
############################################################################### 
#                 Exporting to OpenMC materials.xml file 
###############################################################################
fuel = openmc.Material(material_id=1, name='fuel', temperature=293.6)
fuel.set_density('g/cc', 4.5)
fuel.add_element('U', 0.5, percent_type='wo', enrichment=3)
fuel.add_element('Fe', 0.1, percent_type='wo')
fuel.add_element('Al', 0.1, percent_type='wo')
fuel.add_element('B', 0.1, percent_type='wo')
fuel.add_element('H', 0.1, percent_type='wo')
fuel.add_element('S', 0.1, percent_type='wo')
moderator = openmc.Material(material_id=2, name='moderator', temperature= 293.6)
moderator.set_density('g/cc', 1.0)
moderator.add_element('H', 2, percent_type='ao')   
moderator.add_element('O', 0.8, percent_type='ao')
moderator.add_element('Al', 0.1, percent_type='ao')
moderator.add_element('Fe', 0.1, percent_type='ao')
moderator.add_s_alpha_beta('c_H_in_H2O')
iron = openmc.Material(material_id=3, name='iron', temperature= 293.6)
iron.set_density('g/cc', 7.9)
iron.add_element('Al', 0.3, percent_type='ao')
iron.add_element('B', 0.3, percent_type='ao')
iron.add_element('Cu', 0.4, percent_type='ao', enrichment=60, enrichment_target='Cu63', enrichment_type='wo') 
materials = openmc.Materials([fuel, iron, moderator])
materials.export_to_xml()
############################################################################### 
#                 Exporting to OpenMC geometry.xml file                        
###############################################################################
left= openmc.XPlane(surface_id=1, x0=-30, name='left')
right= openmc.XPlane(surface_id=2, x0=30, name='right')
bottom= openmc.YPlane(surface_id=3, y0=-40, name='bottom')
top= openmc.YPlane(surface_id=4, y0=40, name='top')
fuel_surf= openmc.ZCylinder(surface_id=5, x0=0.0, y0=0.0, r=0.4, name='fuel_surf')
outside_surface =openmc.Sphere(surface_id=6, x0=0., y0=0., z0=0., r=60., name='ouside_surf', boundary_type='vacuum')
Cell2= openmc.Cell(cell_id=2, name='Cell2')
Cell2.region = -fuel_surf
Cell2.fill = fuel
Cell3= openmc.Cell(cell_id=3, name='Cell3')
Cell3.region = +fuel_surf
Cell3.fill = moderator
Cell4= openmc.Cell(cell_id=4, name='Cell4')
Cell4.fill = moderator
Cell5= openmc.Cell(cell_id=5, name='Cell5')
Cell5.region = -fuel_surf
Cell5.fill = fuel
Cell6= openmc.Cell(cell_id=6, name='Cell6')
Cell6.region = +fuel_surf
Cell6.fill = moderator
Univ1 = openmc.Universe(universe_id=1, name='Univ1')
Univ1.add_cells([Cell2,  Cell3])
Univ2 = openmc.Universe(universe_id=2, name='Univ2')
Univ2.add_cells([Cell4])
Univ3 = openmc.Universe(universe_id=3, name='Univ4')
Univ3.add_cells([Cell5,  Cell6])
Lat5= openmc.RectLattice(lattice_id=5)
Lat5.lower_left = [-2.5,-2.5,-3]
Lat5.pitch = [1,1,2]
Lat5.universes = [[[Univ1, Univ1, Univ1, Univ1, Univ1],
                   [Univ1, Univ1, Univ1, Univ1, Univ1],
                   [Univ1, Univ1, Univ2, Univ1, Univ1],
                   [Univ1, Univ1, Univ1, Univ1, Univ1],
                   [Univ1, Univ1, Univ1, Univ1, Univ1]],
                  [[Univ1, Univ3, Univ3, Univ3, Univ3],
                   [Univ3, Univ3, Univ3, Univ3, Univ3],
                   [Univ3, Univ3, Univ1, Univ3, Univ3],
                   [Univ3, Univ3, Univ3, Univ3, Univ3],
                   [Univ3, Univ3, Univ3, Univ3, Univ1]],
                  [[Univ3, Univ1, Univ1, Univ1, Univ1],
                   [Univ1, Univ1, Univ1, Univ1, Univ1],
                   [Univ1, Univ1, Univ3, Univ1, Univ1],
                   [Univ1, Univ1, Univ1, Univ1, Univ1],
                   [Univ1, Univ1, Univ1, Univ1, Univ3]]]
Lat5.outer = Univ2
Lat6= openmc.HexLattice(lattice_id=6)
Lat6.center = [0,0,0]
Lat6.pitch = [1,2]
Lat6.outer = Univ2
Axial1ring0 = [Univ3]*12
Axial1ring1 = [Univ3]*6
Axial1ring2 = [Univ3]
Axial2ring0 = [Univ1]*12
Axial2ring1 = [Univ1]*6
Axial2ring2 = [Univ2]
Axial3ring0 = [Univ3]*12
Axial3ring1 = [Univ3]*6
Axial3ring2 = [Univ2]
Lat6.universes = [[Axial1ring0, Axial1ring1, Axial1ring2],
                  [Axial2ring0, Axial2ring1, Axial2ring2],
                  [Axial3ring0, Axial3ring1, Axial3ring2]]
Cell1= openmc.Cell(cell_id=1, name='Cell1') 
Cell1.region = +left & -right & +bottom & -top & -outside_surface
Cell1.fill = Lat6
Cell10= openmc.Cell(cell_id=10, name='Cell10')
Cell10.region = -outside_surface |(+left & -right & +bottom & -top)
Cell10.fill = moderator
geometry = openmc.Geometry([Cell1, Cell10])
geometry.export_to_xml() 
############################################################################### 
#                 Exporting to OpenMC settings.xml file 
###############################################################################
settings = openmc.Settings()
settings.run_mode = 'fixed source'
settings.particles = 1000000
settings.batches = 10
settings.generations = 10
spatial1 = openmc.stats.Box([ -1, -1, -1], [ 1, 1, 1])
energy1 = openmc.stats.Watt(2, 1)
angle1 = openmc.stats.Isotropic()
source1 = openmc.Source(spatial1, angle1, energy1, strength=1., particle='neutron')
settings.source = [source1]
settings.export_to_xml()
############################################################################### 
#                 Exporting to OpenMC plots.xml file                        
###############################################################################
_plot1 = openmc.Plot(plot_id= 1 )
_plot1.filename = '_plot1'
_plot1.origin = (0,0,0)
_plot1.width = (6,6)
_plot1.pixels = (400,400)
_plot1.color_by = 'material'
_plot1.basis = 'xy'
_plot2 = openmc.Plot(plot_id= 2 )
_plot2.filename = '_plot2'
_plot2.origin = (0,0,0)
_plot2.width = (8,8)
_plot2.pixels = (4000,4000)
_plot2.color_by = 'material'
_plot2.basis = 'yz'
xy_plot3 = openmc.Plot(plot_id= 3 )
xy_plot3.filename = 'xy_plot3'
xy_plot3.origin = (0,0,0)
xy_plot3.width = (10,10)
xy_plot3.pixels = (1000,1000)
xy_plot3.color_by = 'material'
xy_plot3.basis = 'xy'
_plot4 = openmc.Plot(plot_id= 4 )
_plot4.filename = '_plot4'
_plot4.origin = (0,0,0)
_plot4.width = (10,10)
_plot4.pixels = (1000,1000)
_plot4.color_by = 'cell'
_plot4.basis = 'xz'
_plot5 = openmc.Plot(plot_id= 5 )
_plot5.filename = '_plot5'
_plot5.type='voxel'
_plot5.origin = (0,0,0)
_plot5.width = (12,12,24)
_plot5.pixels = (120,120,240)
_plot5.color_by = 'material'
_plot6 = openmc.Plot(plot_id= 6 )
_plot6.filename = '_plot6'
_plot6.origin = (0,0,0)
_plot6.width = (65,85,90)
_plot6.pixels = (60,60,60)
_plot6.type ="voxel"
_plot6.color_by = 'material'
plots = openmc.Plots( [_plot1, _plot2, xy_plot3, _plot4, _plot5, _plot6] )
plots.export_to_xml()
###############################################################################
#                 Exporting to OpenMC tallies.xml file 
###############################################################################
tallies = openmc.Tallies()
_tally1 = openmc.Tally(tally_id=1, name='RR1')
_tally1.scores = ['total']
tallies.append(_tally1)
Energy_filter1 = openmc.EnergyFilter([1E-5, 1E-3, 0.1, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 100.0, 1E3, 1E4, 1E5, 1E6, 2E6], filter_id=1)
_tally2 = openmc.Tally(tally_id=2, name='RR2')
_tally2.scores = ['elastic', 'absorption', '(n,gamma)', 'total']
_tally2.nuclides = ['U235', 'H2', 'Al27', 'Fe56']
tallies.append(_tally2)
Energy_filter2 = openmc.EnergyFilter([0.0001, 0.001, 0.01, 0.1, 1.0, 10.0], filter_id=2)
Cell_filter3 = openmc.CellFilter([Cell1, Cell2, Cell3, Cell4, Cell5, Cell6], filter_id=3)
_tally3 = openmc.Tally(tally_id=3, name='RR3')
_tally3.filters += ([Cell_filter3])
_tally3.scores = ['flux', 'absorption', 'elastic', 'scatter', '(n,p)']
tallies.append(_tally3)
_tally4 = openmc.Tally(tally_id=4, name='RR4')
_tally4.filters += [Energy_filter2]
_tally4.scores = ['flux', 'total', 'absorption']
tallies.append(_tally4)
_tally5 = openmc.Tally(tally_id=5, name='RR5')
_tally5.filters += [Cell_filter3, Energy_filter2]
_tally5.scores = ['flux', 'absorption', 'elastic', 'total', '(n,gamma)']
tallies.append(_tally5)
_tally6 = openmc.Tally(tally_id=6, name='RR6')
_tally6.filters += [Energy_filter1]
_tally6.nuclides = ['U235', 'H1', 'B10', 'Al27', 'Fe56']
_tally6.scores = ['(n,gamma)', 'absorption', 'total']
tallies.append(_tally6)
#
mesh1 = openmc.RegularMesh(mesh_id=1, name='mesh')
mesh1.dimension = [6, 8]
mesh1.lower_left = [-29.0, -41.0]
mesh1.upper_right = [29.0, 41.0]
#
mesh2 = openmc.RectilinearMesh(mesh_id=1)
mesh2.x_grid = [0, 1, 2]
mesh2.y_grid = [0.0, 2.0, 3.0]
mesh2.z_grid = [1.0, 2.0, 3.0]
Mesh_filter4 = openmc.MeshFilter(mesh1, filter_id=4)
_tally7 = openmc.Tally(tally_id=7, name='mesh')
_tally7.filters += [ Mesh_filter4, Energy_filter1]
_tally7.scores = ['flux', 'absorption', 'elastic', '(n,gamma)']
tallies.append(_tally7)
Surface_filter5 = openmc.SurfaceFilter([left, right], filter_id=5)
Surface_filter6 = openmc.SurfaceFilter([bottom, fuel_surf, left, right, top, outside_surface], filter_id=6)
_tally8 = openmc.Tally(tally_id=8, name='current1')
_tally8.filters += [Surface_filter6]
_tally8.scores = ['current']
tallies.append(_tally8)
#
Mesh_filter5 = openmc.MeshFilter(mesh2, filter_id=7)
_tally9 = openmc.Tally(tally_id=9, name='flux')
_tally9.filters.append(Energy_filter1)
_tally9.filters.append(Mesh_filter5)
_tally9.scores = ['flux']
tallies.append(_tally9)
_tally10 = openmc.Tally(tally_id=10, name='RR10')
_tally10.filters += [Energy_filter2, Cell_filter3]
_tally10.scores = ['flux', 'absorption', 'elastic', 'total', '(n,gamma)']
tallies.append(_tally10)
#
_tally11 = openmc.Tally(tally_id=11, name='RR11')
_tally11.scores = ['elastic', 'absorption', '(n,gamma)', 'total']
_tally11.nuclides = ['U235', 'H2', 'Al27', 'total']
tallies.append(_tally11)
#
_tally12 = openmc.Tally(tally_id=12, name='RR12')
_tally12.scores = ['elastic', 'absorption', '(n,gamma)', 'total']
_tally12.nuclides = ['U235', 'H2', 'Al27', 'Fe56']
_tally12.filters += ([Cell_filter3])
tallies.append(_tally12)
_tally13 = openmc.Tally(tally_id=13, name='RR13')
_tally13.scores = ['elastic', 'absorption', '(n,gamma)', 'total']
_tally13.nuclides = ['U235', 'H2', 'Al27', 'Fe56', 'total']
tallies.append(_tally13)
_tally14 = openmc.Tally(tally_id=14, name='RR14')
_tally14.scores = ['elastic', 'absorption', '(n,gamma)', 'total']
_tally14.nuclides = ['U235', 'H2', 'Al27', 'Fe56', 'total']
_tally14.filters += ([Cell_filter3])
tallies.append(_tally14)
_tally15 = openmc.Tally(tally_id=15, name='RR15')
_tally15.scores = ['elastic', 'absorption', '(n,gamma)', '(n,p)', 'scatter', 'total']
_tally15.nuclides = ['U235', 'H2', 'Al27', 'Fe56', 'total']
_tally15.filters += ([Cell_filter3])
tallies.append(_tally15)
Surface_filter8 = openmc.SurfaceFilter([bottom, fuel_surf, left, right, top], filter_id=8)
_tally18 = openmc.Tally(tally_id=18, name='Flux Current')
_tally18.filters += [Surface_filter8, Energy_filter2]
_tally18.scores = ['current']
tallies.append(_tally18)
_tally19 = openmc.Tally(tally_id=19, name='Mesh by Nuclide')
_tally19.filters += [Mesh_filter4]
_tally19.nuclides = ['Al27', 'Fe56', 'U235', 'U238']
_tally19.scores = ['absorption', 'elastic', 'total']
tallies.append(_tally19)
Mu = np.linspace(-1, 1, 5, endpoint=True)
Mu_filter9 = openmc.MuFilter(Mu, filter_id=9)
_tally20 = openmc.Tally(tally_id=20, name='Cosine')
_tally20.filters += [Surface_filter8, Mu_filter9]
_tally20.scores = ['current']
tallies.append(_tally20)
_tally21 = openmc.Tally(tally_id=21, name='Cosine and energy')
_tally21.filters += [Energy_filter2, Surface_filter8, Mu_filter9]
_tally21.scores = ['current']
tallies.append(_tally21)
_tally22 = openmc.Tally(tally_id=22, name='mesh only')
_tally22.filters += [Mesh_filter4]
_tally22.scores = ['flux', 'absorption', 'elastic', 'total']
tallies.append(_tally22)
mesh3 = openmc.RegularMesh(mesh_id=3)
mesh3.dimension = [16, 16, 5]
mesh3.lower_left = [-29.0, -41.0, -3.0]
mesh3.upper_right = [29.0, 41.0, 3.0]
Mesh_filter10 = openmc.MeshFilter(mesh3, filter_id=10)
_tally23 = openmc.Tally(tally_id=23, name='mesh 3D')
_tally23.filters += [Mesh_filter10]
_tally23.scores = ['flux', 'total']
tallies.append(_tally23)
_tally24 = openmc.Tally(tally_id=24, name='mu tally')
_tally24.filters += [Mu_filter9]
_tally24.scores = ['flux']
tallies.append(_tally24)
_tally25 = openmc.Tally(tally_id=25, name='mu scatter')
_tally25.filters += [Mu_filter9]
_tally25.nuclides = ['U235', 'U238']
_tally25.scores = ['scatter', 'fission']
tallies.append(_tally25)
tallies.export_to_xml()
#openmc.plot_geometry()
openmc.run()