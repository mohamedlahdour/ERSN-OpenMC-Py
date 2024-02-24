#%matplotlib inline
import openmc
import numpy as np
import matplotlib.pyplot as plt
# Define fuel and B4C materials
fuel = openmc.Material()
fuel.add_element('U', 1.0, enrichment=4.5)
fuel.add_nuclide('O16', 2.0)
fuel.set_density('g/cm3', 10.0)
b4c = openmc.Material()
b4c.add_element('B', 4.0)
b4c.add_element('C', 1.0)
b4c.set_density('g/cm3', 2.5)
# Define surfaces used to construct regions
zmin, zmax = -10., 10.
boron_lower = openmc.ZPlane(z0=-0.5)  
box = openmc.model.RectangularPrism(10., 10., boundary_type='reflective')
box2 = openmc.model.HexagonalPrism(edge_length=1., orientation='y', origin=(0., 0.),
                    boundary_type='transmission', corner_radius=0.)
bottom = openmc.ZPlane(z0=zmin, boundary_type='vacuum')
boron_upper = openmc.ZPlane(z0=0.5)
top = openmc.ZPlane(z0=zmax, boundary_type='vacuum')
# Create three cells and add them to geometry
fuel1 = openmc.Cell(fill=fuel, region=-box & +bottom & -boron_lower)
absorber = openmc.Cell(fill=b4c, region=-box & +boron_lower & -boron_upper)   
fuel2 = openmc.Cell(fill=fuel, region=-box & +boron_upper & -top)
geom = openmc.Geometry([fuel1, absorber, fuel2])
settings = openmc.Settings()
spatial_dist = openmc.stats.Box(*geom.bounding_box)
settings.source = openmc.Source(space=spatial_dist)
settings.batches = 210
settings.inactive = 10
settings.particles = 1000
# Create a flux tally
flux_tally = openmc.Tally()
flux_tally.scores = ['flux']
# Create a Legendre polynomial expansion filter and add to tally
order = 8
expand_filter = openmc.SpatialLegendreFilter(order, 'z', zmin, zmax)
flux_tally.filters.append(expand_filter)
tallies = openmc.Tallies([flux_tally])
model = openmc.model.Model(geometry=geom, settings=settings, tallies=tallies)
model.run(output=False)