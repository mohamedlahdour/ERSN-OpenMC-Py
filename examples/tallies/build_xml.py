import openmc
import openmc.lib
import numpy as np
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
moderator = openmc.Material(material_id=2, name='moderator', temperature= 293.6)
moderator.set_density('g/cc', 0.9999)
moderator.add_element('H', 2, percent_type='ao')
moderator.add_element('O', 0.8, percent_type='ao')
moderator.add_element('Al', 0.011, percent_type='ao')
moderator.add_element('Fe', 0.01, percent_type='ao')
moderator.add_s_alpha_beta('c_H_in_H2O')
iron = openmc.Material(material_id=3, name='iron', temperature= 293.6)
iron.set_density('g/cc', 7.899)
iron.add_element('Al', 0.299, percent_type='wo')
iron.add_element('B', 0.001, percent_type='wo')
iron.add_element('Fe', 0.5, percent_type='wo')
iron.add_element('Cu', 0.2, percent_type='wo', enrichment=23, enrichment_target='Cu65', enrichment_type='wo') 
iron.add_s_alpha_beta('c_Fe56')
fuel = openmc.Material(material_id=1, name='fuel', temperature= 293.6)
fuel.set_density('g/cc', 10.5)
fuel.add_element('U', 0.5, percent_type='wo', enrichment=20) #, enrichment_target='U235', enrichment_type='wo') 
fuel.add_element('Fe', 0.1, percent_type='wo')
fuel.add_element('Al', 0.099, percent_type='wo')
fuel.add_element('B', 0.001, percent_type='wo')
fuel.add_element('H', 0.2, percent_type='wo')
fuel.add_element('S', 0.1, percent_type='wo')
materials = openmc.Materials([moderator, iron, fuel])
materials.export_to_xml()
############################################################################### 
#                 Exporting to OpenMC geometry.xml file                        
###############################################################################
left= openmc.XPlane(surface_id=1, x0=-50, name='left')
right= openmc.XPlane(surface_id=2, x0=50, name='right')
bottom= openmc.YPlane(surface_id=3, y0=-50, name='bottom')
top= openmc.YPlane(surface_id=4, y0=50, name='top')
fuel_surf= openmc.ZCylinder(surface_id=5, x0=0.0, y0=0.0, r=1.2, name='fuel_surf')
outside_surface =openmc.Sphere(surface_id=6, x0=0., y0=0., z0=0., r=120., name='ouside_surf', boundary_type='vacuum')
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
Cell5.fill = iron
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
Axial1ring0 = [Univ3]*18
Axial1ring1 = [Univ3]*12
Axial1ring2 = [Univ3]*6
Axial1ring3 = [Univ3]
Axial2ring0 = [Univ1]*18
Axial2ring1 = [Univ1]*12
Axial2ring2 = [Univ1]*6
Axial2ring3 = [Univ2]
Axial3ring0 = [Univ3]*18
Axial3ring1 = [Univ3]*12
Axial3ring2 = [Univ3]*6
Axial3ring3 = [Univ2]
Lat6.universes = [[Axial1ring0, Axial1ring1, Axial1ring2, Axial1ring3],
                  [Axial2ring0, Axial2ring1, Axial2ring2, Axial2ring3],
                  [Axial3ring0, Axial3ring1, Axial3ring2, Axial3ring3]]
Lat7= openmc.HexLattice(lattice_id=7)
Lat7.center = [0,0]
Lat7.pitch = [3]
Lat7.outer = Univ2
ring0 = [Univ1]*48
ring1 = [Univ3]*42
ring2 = [Univ1]*36
ring3 = [Univ3]*30
ring4 = [Univ1]*24
ring5 = [Univ3]*18
ring6 = [Univ1]*12
ring7 = [Univ3]*6
ring8 = [Univ2]
Lat7.universes = [ring0, ring1, ring2, ring3, ring4, ring5, ring6, ring7, ring8]
Lat7.orientation = 'y'
Cell1= openmc.Cell(cell_id=1, name='Cell1') 
Cell1.region = +left & -right & +bottom & -top & -outside_surface
Cell1.fill = Lat7
Cell10= openmc.Cell(cell_id=10, name='Cell10')
Cell10.region = -outside_surface |(+left & -right & +bottom & -top)
Cell10.fill = moderator
geometry = openmc.Geometry([Cell1, Cell10])
geometry.export_to_xml() 
############################################################################### 
#                 Exporting to OpenMC settings.xml file 
###############################################################################
settings = openmc.Settings()
spatial1 = openmc.stats.Box([ -7, -7, -7], [ 7, 7, 7])
energy1 = openmc.stats.Maxwell(0.025)
angle1 = openmc.stats.Isotropic()
source1 = openmc.Source(spatial1, angle1, energy1, strength=1., particle='neutron')
settings.source = [source1]
settings.run_mode = 'eigenvalue'
settings.particles = 10000
settings.batches = 310
settings.inactive = 10
settings.generations = 1
#settings.photon_transport = True
#settings.cutoff = {'energy_photon' : 1000.0 }
#settings.electron_treatment = 'led'
#
entropy_mesh = openmc.RegularMesh()
entropy_mesh.lower_left = (-50, -50, -120)
entropy_mesh.upper_right = (50, 50, 120)
entropy_mesh.dimension = (10, 10, 10)
settings.entropy_mesh = entropy_mesh
settings.export_to_xml()
############################################################################### 
#                 Exporting to OpenMC plots.xml file                        
###############################################################################
_plot1 = openmc.Plot(plot_id= 1 )
_plot1.filename = '_plot1'
_plot1.origin = (0,0,0)
_plot1.width = (60,60)
_plot1.pixels = (600,600)
_plot1.color_by = 'material'
_plot1.basis = 'xy'
_plot2 = openmc.Plot(plot_id= 2 )
_plot2.filename = '_plot2'
_plot2.origin = (0,0,0)
_plot2.width = (60,80)
_plot2.pixels = (600,800)
_plot2.color_by = 'material'
_plot2.basis = 'yz'
_plot4 = openmc.Plot(plot_id= 4 )
_plot4.filename = '_plot4'
_plot4.origin = (0,0,0)
_plot4.width = (60,80)
_plot4.pixels = (600,800)
_plot4.color_by = 'cell'
_plot4.basis = 'xz'
_plot5 = openmc.Plot(plot_id= 5 )
_plot5.filename = '_plot5'
_plot5.type='voxel'
_plot5.origin = (0,0,0)
_plot5.width = (60,60,80)
_plot5.pixels = (120,120,160)
_plot5.color_by = 'material'
plots = openmc.Plots( [_plot1, _plot2, _plot4, _plot5] )
plots.export_to_xml()
###############################################################################
#                 Exporting to OpenMC tallies.xml file 
###############################################################################
# filters
Energy_filter1 = openmc.EnergyFilter([1E-5, 1E-3, 0.1, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 100.0, 1E3, 1E4, 1E5, 1E6, 2E6], filter_id=1)
Energy_filter2 = openmc.EnergyFilter([0.0001, 0.001, 0.01, 0.1, 1.0, 10.0], filter_id=2)
Cell_filter3 = openmc.CellFilter([Cell1, Cell2, Cell3, Cell4, Cell5, Cell6], filter_id=3)
Energyout_filter4 = openmc.EnergyoutFilter([0.0001, 0.001, 0.01, 0.1, 1.0, 10.0], filter_id=4)
Surface_filter5 = openmc.SurfaceFilter([left, right], filter_id=5)
Universe_filter8 = openmc.UniverseFilter([Univ1, Univ2, Univ3], filter_id=8)
Mu = np.linspace(-1, 1, 10, endpoint=True)
Mu_filter9 = openmc.MuFilter(Mu, filter_id=9)
CellFrom_filter11 = openmc.CellFromFilter([Cell1, Cell2, Cell3, Cell4, Cell5], filter_id=11)
CellBorn_filter12 = openmc.CellbornFilter([Cell1, Cell2, Cell3, Cell4, Cell5], filter_id=12)
Collision_filter13 = openmc.CollisionFilter([1, 2, 3, 4], filter_id=13)
Particle_filter14 = openmc.ParticleFilter(['neutron'], filter_id=14)
Material_filter10 = openmc.MaterialFilter([moderator, iron, fuel], filter_id=15)
# extra filters
Polar = np.linspace(0, np.pi, 10, endpoint=True)
Polar_filter16 = openmc.PolarFilter(Polar, filter_id=16)
Azimuthal = np.linspace(-np.pi, np.pi, 10, endpoint=True)
Azimuthal_filter17 = openmc.AzimuthalFilter(Azimuthal, filter_id=17)
Distribcell_filter18 = openmc.DistribcellFilter(Cell2, filter_id=18)
Legendre_filter19 = openmc.LegendreFilter(order= 3, filter_id=19)
zmin =  -1
zmax =  1
SpatialLegendre_filter20 = openmc.SpatialLegendreFilter(order= 3, axis='z', minimum=zmin, maximum=zmax, filter_id=20)
SphericalHarmonics_filter21 = openmc.SphericalHarmonicsFilter(order= 4, filter_id=21)
Time_filter22 = openmc.TimeFilter([1, 2, 3], filter_id=22)
DelayedGroup_filter22 = openmc.DelayedGroupFilter([1, 2, 3, 4, 5, 6], filter_id=23)
Zernike_filter24 = openmc.ZernikeFilter(order= 3, x= 0, y= 0, r= 1, filter_id=24)
ZernikeRadial_filter25 = openmc.ZernikeRadialFilter(order= 3, x= 0, y= 0, r= 1, filter_id=25)
Particle_filter30 = openmc.ParticleFilter(['neutron', 'photon'], filter_id=30)
#
# Unfiltered
tallies = openmc.Tallies()
_tally1 = openmc.Tally(tally_id=1, name='RR1')
_tally1.scores = ['total']
tallies.append(_tally1)
#
_tally2 = openmc.Tally(tally_id=2, name='RR2')
_tally2.scores = ['elastic', '(n,p)', '(n,gamma)']
_tally2.nuclides = ['U235', 'H1', 'Al27', 'Fe56']
tallies.append(_tally2)
tallies.export_to_xml()
#
# One filter
_tally3 = openmc.Tally(tally_id=3, name='RR3')
_tally3.filters += ([Cell_filter3])
_tally3.scores = ['flux', 'absorption', 'elastic', 'scatter', '(n,p)']
tallies.append(_tally3)
#
_tally4 = openmc.Tally(tally_id=4, name='RR4')
_tally4.scores = ['elastic', 'absorption', '(n,gamma)', 'total']
_tally4.nuclides = ['U235', 'H1', 'Al27', 'Fe56']
_tally4.filters += ([Cell_filter3])
tallies.append(_tally4)
#
_tally5 = openmc.Tally(tally_id=5, name='RR5')
_tally5.filters += [Energy_filter2]
_tally5.scores = ['flux', 'total', 'absorption']
tallies.append(_tally5)
#
_tally6 = openmc.Tally(tally_id=6, name='RR6')
_tally6.filters += [Energy_filter1]
_tally6.nuclides = ['U235', 'H1', 'B10', 'Al27', 'Fe56']
_tally6.scores = ['(n,gamma)', 'absorption', 'total']
tallies.append(_tally6)
#
_tally7 = openmc.Tally(tally_id=7, name='current1')
_tally7.filters += [Surface_filter5]
_tally7.scores = ['current']
tallies.append(_tally7)
#
_tally8 = openmc.Tally(tally_id=8, name='mu tally')
_tally8.filters += [Mu_filter9]
_tally8.scores = ['flux']
tallies.append(_tally8)
#
_tally9 = openmc.Tally(tally_id=9, name='mu scatter')
_tally9.filters += [Mu_filter9]
_tally9.nuclides = ['U235', 'U238']
_tally9.scores = ['scatter', 'fission']
tallies.append(_tally9)
#
_tally10 = openmc.Tally(tally_id=10, name='RR10')
_tally10.filters += [Universe_filter8]
_tally10.nuclides = ['H1', 'U235', 'U238']
_tally10.scores = ['scatter', 'fission']
tallies.append(_tally10)
#
_tally11 = openmc.Tally(tally_id=11, name='RR11')
_tally11.filters += [Material_filter10]
_tally11.nuclides = ['H1', 'Fe56', 'U235', 'U238']
_tally11.scores = ['scatter', 'absorption', 'total']
tallies.append(_tally11)
#
_tally12 = openmc.Tally(tally_id=12, name='RR12')
_tally12.filters += [CellFrom_filter11]
_tally12.nuclides = ['H1', 'Fe56', 'U235', 'U238']
_tally12.scores = ['scatter', 'absorption', 'total']
tallies.append(_tally12)
#
_tally13 = openmc.Tally(tally_id=13, name='RR13')
_tally13.filters += [CellBorn_filter12]
_tally13.nuclides = ['H1', 'Fe56', 'U235', 'U238']
_tally13.scores = ['scatter', 'absorption', 'total']
tallies.append(_tally13)
#
_tally14 = openmc.Tally(tally_id=14, name='RR14')
_tally14.filters += [Particle_filter14]
_tally14.nuclides = ['H1', 'Fe56', 'U235', 'U238']
_tally14.scores = ['scatter', 'absorption', 'total']
tallies.append(_tally14)
#
_tally15 = openmc.Tally(tally_id=15, name='RR15')
_tally15.filters += [Collision_filter13]
_tally15.nuclides = ['H1', 'Fe56', 'U235', 'U238']
_tally15.scores = ['scatter', 'absorption', 'total']
tallies.append(_tally15)
#
_tally16 = openmc.Tally(tally_id=16, name='RR16')
_tally16.filters += [Energyout_filter4]
_tally16.scores = ['scatter', 'nu-fission']
tallies.append(_tally16)
#
_tally17 = openmc.Tally(tally_id=17, name='RR17')
_tally17.filters += [Energyout_filter4]
_tally17.nuclides = ['H1', 'Fe56', 'U235', 'U238']
_tally17.scores = ['scatter', 'nu-fission']
tallies.append(_tally17)
#
_tally18 = openmc.Tally(tally_id=18, name='RR18')
_tally18.filters += [Polar_filter16]
_tally18.nuclides = ['H1', 'Fe56', 'U235', 'U238']
_tally18.scores = ['scatter', 'nu-fission']
tallies.append(_tally18)
#
_tally19 = openmc.Tally(tally_id=19, name='RR19')
_tally19.filters += [Azimuthal_filter17]
_tally19.nuclides = ['H1', 'Fe56', 'U235', 'U238']
_tally19.scores = ['scatter', 'nu-fission']
tallies.append(_tally19)
#
# Two filters
_tally20 = openmc.Tally(tally_id=20, name='RR20')
_tally20.filters += [Cell_filter3, Energy_filter2]
_tally20.scores = ['flux', 'absorption', 'elastic', 'total', '(n,gamma)']
tallies.append(_tally20)
#
_tally21 = openmc.Tally(tally_id=21, name='RR21')
_tally21.filters += [Energy_filter2, Cell_filter3]
_tally21.scores = ['flux', 'absorption', 'elastic', 'total', '(n,gamma)']
tallies.append(_tally21)
#
_tally22 = openmc.Tally(tally_id=22, name='RR22')
_tally22.nuclides = ['H1', 'U235', 'U238']
_tally22.filters += [Cell_filter3, Energy_filter2]
_tally22.scores = ['absorption', 'elastic', 'total', '(n,gamma)']
tallies.append(_tally22)
#
_tally23 = openmc.Tally(tally_id=23, name='RR23')
_tally23.nuclides = ['H1', 'U235', 'U238']
_tally23.filters += [Cell_filter3, Mu_filter9]
_tally23.scores = ['scatter', 'nu-scatter','elastic', 'fission', 'nu-fission']
tallies.append(_tally23)
#
_tally24 = openmc.Tally(tally_id=24, name='RR24')
_tally24.filters += [Cell_filter3, Surface_filter5]
_tally24.scores = ['current']
tallies.append(_tally24)
#
_tally25 = openmc.Tally(tally_id=25, name='Current')
_tally25.filters += [Surface_filter5, Energy_filter2]
_tally25.scores = ['current']
tallies.append(_tally25)
#
_tally26 = openmc.Tally(tally_id=26, name='Cosine')
_tally26.filters += [Surface_filter5, Mu_filter9]
_tally26.scores = ['current']
tallies.append(_tally26)
#
_tally27 = openmc.Tally(tally_id=27, name='RR27')
_tally27.nuclides = ['H1', 'U235', 'U238']
_tally27.filters += [Energy_filter2, Mu_filter9]
_tally27.scores = ['scatter', 'nu-scatter','elastic', 'fission', 'nu-fission']
tallies.append(_tally27)
#
_tally28 = openmc.Tally(tally_id=28, name='RR28')
_tally28.nuclides = ['H1', 'U235', 'U238']
_tally28.filters += [Energy_filter2, Universe_filter8]
_tally28.scores = ['scatter', 'nu-scatter','elastic', 'fission', 'nu-fission']
tallies.append(_tally28)
#
_tally29 = openmc.Tally(tally_id=29, name='RR29')
_tally29.filters += [Material_filter10, Energy_filter2]
_tally29.scores = ['flux', 'absorption', 'elastic', 'total', '(n,gamma)']
tallies.append(_tally29)
#
_tally30 = openmc.Tally(tally_id=30, name='RR30')
_tally30.filters += [Energy_filter2, CellFrom_filter11]
_tally30.scores = ['flux']
tallies.append(_tally30)
#
_tally31 = openmc.Tally(tally_id=31, name='RR31')
_tally31.filters += [Cell_filter3, CellBorn_filter12]
_tally31.scores = ['flux', 'scatter']
tallies.append(_tally31)
#
_tally32 = openmc.Tally(tally_id=32, name='RR32')
_tally32.filters += [Energy_filter2, CellFrom_filter11]
_tally32.scores = ['flux', 'absorption', 'total']
tallies.append(_tally32)
#
_tally33 = openmc.Tally(tally_id=33, name='RR33')
_tally33.filters += [Mu_filter9, CellFrom_filter11]
_tally33.scores = ['flux']
tallies.append(_tally33)
#
_tally34 = openmc.Tally(tally_id=34, name='RR34')
_tally34.filters += [Cell_filter3, Polar_filter16]
_tally34.scores = ['flux', 'scatter']
tallies.append(_tally34)
#
_tally35 = openmc.Tally(tally_id=35, name='RR35')
_tally35.filters += [Cell_filter3, Azimuthal_filter17]
_tally35.scores = ['flux', 'scatter']
tallies.append(_tally35)
#
_tally36 = openmc.Tally(tally_id=36, name='RR36')
_tally36.filters += [Energy_filter1, Polar_filter16]
_tally36.scores = ['flux', 'scatter']
tallies.append(_tally36)
#
_tally37 = openmc.Tally(tally_id=37, name='RR37')
_tally37.filters += [Energy_filter1, Azimuthal_filter17]
_tally37.scores = ['flux', 'scatter']
tallies.append(_tally37)
#
_tally38 = openmc.Tally(tally_id=38, name='RR38')
_tally38.filters += [Energyout_filter4, Polar_filter16]
_tally38.scores = ['elastic', 'scatter']
tallies.append(_tally38)
#
# Three filters
_tally41 = openmc.Tally(tally_id=41, name='RR41')
_tally41.filters += [Cell_filter3, Energy_filter2, Surface_filter5]
_tally41.scores = ['current']
tallies.append(_tally41)
#
_tally42 = openmc.Tally(tally_id=42, name='RR42')
_tally42.filters += [Cell_filter3, Energy_filter2, Mu_filter9]
_tally42.scores = ['flux', 'scatter', 'fission', 'nu-fission']
tallies.append(_tally42)
#
_tally43 = openmc.Tally(tally_id=43, name='RR43')
_tally43.filters += [Cell_filter3, Surface_filter5, Mu_filter9]
_tally43.scores = ['current']
tallies.append(_tally43)
#
_tally44 = openmc.Tally(tally_id=44, name='RR44')
_tally44.filters += [Energy_filter2, Surface_filter5, Mu_filter9]
_tally44.scores = ['current']
tallies.append(_tally44)
#
_tally45 = openmc.Tally(tally_id=45, name='RR45')
_tally45.filters += [Energy_filter2, Universe_filter8, Mu_filter9]
_tally45.scores = ['flux', 'scatter', 'fission', 'nu-fission']
tallies.append(_tally45)
#
_tally46 = openmc.Tally(tally_id=46, name='RR46')
_tally46.filters += [Energy_filter2, Material_filter10, Mu_filter9]
_tally46.scores = ['flux', 'scatter', 'fission', 'nu-fission']
tallies.append(_tally46)
#
_tally47 = openmc.Tally(tally_id=47, name='RR47')
_tally47.filters += [Cell_filter3, Energy_filter2, Mu_filter9]
_tally47.scores = ['scatter', 'fission', 'nu-fission']
_tally47.nuclides = ['H1', 'U235', 'U238']
tallies.append(_tally47)
#
# Four filters
#
_tally60 = openmc.Tally(tally_id=60, name='RR60')
_tally60.filters += [Cell_filter3, Energy_filter2, Universe_filter8, Mu_filter9]
_tally60.scores = ['scatter', 'fission', 'nu-fission']
_tally60.nuclides = ['H1', 'U235', 'U238']
tallies.append(_tally60)
#
_tally61 = openmc.Tally(tally_id=61, name='RR61')
_tally61.filters += [Cell_filter3, Energy_filter2, Surface_filter5, Mu_filter9]
_tally61.scores = ['current']
tallies.append(_tally61)
#
_tally62 = openmc.Tally(tally_id=62, name='RR62')
_tally62.filters += [Cell_filter3, Energy_filter2, Material_filter10, Mu_filter9]
_tally62.scores = ['flux', 'scatter', 'fission', 'nu-fission']
tallies.append(_tally62)
#
_tally63 = openmc.Tally(tally_id=63, name='RR63')
_tally63.filters += [Cell_filter3, Energy_filter2, CellFrom_filter11, Mu_filter9]
_tally63.scores = ['scatter', 'fission', 'nu-fission']
tallies.append(_tally63)
#
_tally64 = openmc.Tally(tally_id=64, name='RR64')
_tally64.filters += [Cell_filter3, Energy_filter2, CellBorn_filter12, Mu_filter9]
_tally64.scores = ['flux', 'scatter', 'fission', 'nu-fission']
tallies.append(_tally64)
#
_tally65 = openmc.Tally(tally_id=65, name='RR65')
_tally65.filters = [Cell_filter3, Energy_filter2, Energyout_filter4, Polar_filter16]
_tally65.scores = ['elastic', 'nu-fission']
_tally65.nuclides = ['H1', 'U235', 'U238']
tallies.append(_tally65)
#
_tally80 = openmc.Tally(tally_id=80, name='RR80')
_tally80.filters = [Cell_filter3, Energy_filter2, Energyout_filter4, Polar_filter16, Particle_filter14]
_tally80.scores = ['elastic', 'nu-fission']
_tally80.nuclides = ['H1', 'U235', 'U238']
tallies.append(_tally80)
#
_tally81 = openmc.Tally(tally_id=81, name='RR81')
_tally81.filters = [Cell_filter3, Energy_filter2, Energyout_filter4, Polar_filter16, Mu_filter9]
_tally81.scores = ['elastic', 'nu-fission']
_tally81.nuclides = ['H1', 'U235', 'U238']
tallies.append(_tally81)
#
_tally85 = openmc.Tally(tally_id=85, name='RR85')
_tally85.filters = [Cell_filter3, Energy_filter2, Energyout_filter4, Polar_filter16, Mu_filter9, Particle_filter14]
_tally85.scores = ['elastic', 'nu-fission']
_tally85.nuclides = ['H1', 'U235', 'U238']
tallies.append(_tally85)
#
_tally101 = openmc.Tally(tally_id=101, name='Polar filter')
_tally101.filters = [Polar_filter16]
_tally101.scores = ['flux', 'elastic', 'fission']
tallies.append(_tally101)
#
_tally102 = openmc.Tally(tally_id=102, name='polar filt Isotope')
_tally102.filters = [Polar_filter16]
_tally102.nuclides = ['U235', 'H1']
_tally102.scores = ['elastic', 'fission']
tallies.append(_tally102)
#
_tally103 = openmc.Tally(tally_id=103, name='Azim filter')
_tally103.filters = [Azimuthal_filter17]
_tally103.scores = ['fission', 'elastic']
tallies.append(_tally103)
#
_tally104 = openmc.Tally(tally_id=104, name='Azimut filt isotope')
_tally104.filters = [Azimuthal_filter17]
_tally104.nuclides = ['H1', 'U235']
_tally104.scores = ['fission', 'elastic']
tallies.append(_tally104)
#
_tally105 = openmc.Tally(tally_id=105, name='Disttrib Cell')
_tally105.filters = [ Distribcell_filter18]
_tally105.scores = ['fission', 'elastic', 'flux']
tallies.append(_tally105)
#
_tally106 = openmc.Tally(tally_id=106, name='Distrib Cell isotop')
_tally106.filters = [Distribcell_filter18]
_tally106.nuclides = ['H1', 'U235']
_tally106.scores = ['fission', 'elastic']
tallies.append(_tally106)
#
_tally107 = openmc.Tally(tally_id=107, name='Legend')
_tally107.filters = [Legendre_filter19]
_tally107.scores = ['fission', 'elastic', 'flux']
tallies.append(_tally107)
#
_tally108 = openmc.Tally(tally_id=108, name='Legend isotop')
_tally108.filters = [Legendre_filter19]
_tally108.nuclides = ['H1', 'U235']
_tally108.scores = ['elastic', 'fission']
tallies.append(_tally108)
#
_tally109 = openmc.Tally(tally_id=109, name='Spa Leg')
_tally109.filters = [SpatialLegendre_filter20]
_tally109.scores = ['elastic', 'fission', 'flux']
tallies.append(_tally109)
#
_tally110 = openmc.Tally(tally_id=110, name='Spac LEg isotop')
_tally110.filters = [SpatialLegendre_filter20]
_tally110.nuclides = ['H1', 'U235']
_tally110.scores = ['elastic', 'fission']
tallies.append(_tally110)
#
_tally111 = openmc.Tally(tally_id=111, name='SphHarmonic')
_tally111.filters = [SphericalHarmonics_filter21]
_tally111.scores = ['flux', 'elastic', 'fission']
tallies.append(_tally111)
#
_tally112 = openmc.Tally(tally_id=112, name='Sph Harm iso')
_tally112.nuclides = ['H1', 'U235']
_tally112.scores = ['elastic', 'fission']
_tally112.filters = [SphericalHarmonics_filter21]
tallies.append(_tally112)
#
_tally220 = openmc.Tally(tally_id=220, name='RR220')
_tally220.filters += [Time_filter22]
_tally220.nuclides = ['H1', 'U235', 'U238']
_tally220.scores = ['scatter', 'absorption']
tallies.append(_tally220)
#
_tally221 = openmc.Tally(tally_id=221, name='RR221')
_tally221.filters += [DelayedGroup_filter22]
_tally221.nuclides = ['U235', 'U238']
_tally221.scores = ['decay-rate', 'delayed-nu-fission']
tallies.append(_tally221)
#
_tally222 = openmc.Tally(tally_id=222, name='RR222')
_tally222.filters += [Zernike_filter24]
_tally222.nuclides = ['H1', 'U235', 'U238']
_tally222.scores = ['scatter', 'absorption']
tallies.append(_tally222)
#
_tally223 = openmc.Tally(tally_id=223, name='RR223')
_tally223.filters += [ZernikeRadial_filter25]
_tally223.nuclides = ['U235', 'U238']
_tally223.scores = ['decay-rate', 'delayed-nu-fission']
tallies.append(_tally223)
#
_tally300 = openmc.Tally(tally_id=300, name='Heating')
_tally300.scores = ['heating']
tallies.append(_tally300)
#
_tally301 = openmc.Tally(tally_id=301, name='Heating n p')
_tally301.filters += [Particle_filter30]
_tally301.scores = ['heating']
tallies.append(_tally301)
#
_tally302 = openmc.Tally(tally_id=302, name='Heating-local n p')
_tally302.filters += [Particle_filter30]
_tally302.scores = ['heating-local']
tallies.append(_tally302)
#
_tally303 = openmc.Tally(tally_id=303, name='RR303')
_tally303.scores = ['elastic', '(n,p)', '(n,gamma)', 'scatter']
_tally303.nuclides = ['U235', 'H1', 'Al27', 'Fe56']
_tally303.filters += [Particle_filter30]
tallies.append(_tally303)
#
_tally304 = openmc.Tally(tally_id=304, name='RR304')
_tally304.scores = ['elastic', 'absorption', '(n,gamma)', 'total']
_tally304.nuclides = ['U235', 'H1', 'Al27', 'Fe56']
_tally304.filters += [Particle_filter14]
tallies.append(_tally304)
tallies.export_to_xml()
###############################################################################
#openmc.plot_geometry()
openmc.run()