from pprint import pprint

#%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import openmc
import openmc.lib

fuel = openmc.Material(name='fuel')
fuel.add_nuclide('U235', 1.0)
fuel.set_density('g/cm3', 10.0)

water = openmc.Material(name='water')
water.add_nuclide('H1', 2.0)
water.add_nuclide('O16', 1.0)
water.set_density('g/cm3', 1.0)

mats = openmc.Materials((fuel, water))
mats.export_to_xml()

r_pin = openmc.ZCylinder(r=0.25)
fuel_cell = openmc.Cell(fill=fuel, region=-r_pin)
water_cell = openmc.Cell(fill=water, region=+r_pin)
pin_universe = openmc.Universe(cells=(fuel_cell, water_cell))

all_water_cell = openmc.Cell(fill=water)
water_universe = openmc.Universe(cells=(all_water_cell,))

lat = openmc.HexLattice()
lat.center = (0., 0.)
lat.pitch = [1.25]
lat.outer = water_universe
outer_ring = [pin_universe]*12
middle_ring = [pin_universe]*6
inner_ring = [pin_universe]
lat.universes = [outer_ring, middle_ring, inner_ring]

outer_radius = 4.0
outer_surface = openmc.ZCylinder(r=outer_radius, boundary_type='vacuum')
main_cell = openmc.Cell(fill=lat, region=-outer_surface)
geom = openmc.Geometry([main_cell])
geom.export_to_xml()

p = openmc.Plot.from_geometry(geom)
p.color_by = 'material'
p.colors = {
    fuel: 'yellow',
    water: 'blue'
}
#p.to_ipython_image()

settings = openmc.Settings()
settings.batches = 25
settings.inactive = 5
settings.particles = 10000
settings.source = openmc.Source(space=openmc.stats.Point((0., 0., 0.)))
settings.export_to_xml()

tally = openmc.Tally()
tally.filters = [openmc.DistribcellFilter(fuel_cell)]
tally.scores = ['flux']

tallies = openmc.Tallies([tally])
tallies.export_to_xml()

#openmc.run()

with openmc.StatePoint('statepoint.25.h5') as sp:
    # Get the Tally object
    t = sp.tallies[1]
    
    # Get the mean value of the flux for each instance of the fuel cell as a flattened (1D) numpy array
    flux = t.mean.ravel()
    
    # Show a Pandas dataframe
    df = t.get_pandas_dataframe()    
    print(df)


resolution = (600, 600)
img = np.full(resolution, np.nan)
xmin, xmax = -3., 3.
ymin, ymax = -3., 3.

with openmc.lib.run_in_memory():
    for row, y in enumerate(np.linspace(ymin, ymax, resolution[0])):
        for col, x in enumerate(np.linspace(xmin, xmax, resolution[1])):
            try:
                # For each (x, y, z) point, determine the cell and distribcell index
                cell, distribcell_index = openmc.lib.find_cell((x, y, 0.))
            except openmc.exceptions.GeometryError:
                # If a point appears outside the geometry, you'll get a GeometryError exception.
                # These lines catch the exception and continue on
                continue

            if cell.id == fuel_cell.id:
                # When the cell ID matches, we set the corresponding pixel in the image using the
                # distribcell index. Note that we're taking advantage of the fact that the i-th element
                # in the flux array corresponds to the i-th distribcell instance.
                img[row, col] = flux[distribcell_index]

options = {
    'origin': 'lower',
    'extent': (xmin, xmax, ymin, ymax),
    'vmin': 0.03,
    'vmax': 0.06,
    'cmap': 'RdYlBu_r',
}
plt.imshow(img, **options)
plt.xlabel('x [cm]')
plt.ylabel('y [cm]')
plt.colorbar()

# Create a cell instance
cell_instances = [(fuel_cell, i) for i in range(0, 18, 2)]
cellinst_filter = openmc.CellInstanceFilter(cell_instances)

instance_tally = openmc.Tally()
instance_tally.filters = [cellinst_filter]
instance_tally.scores = ['flux']

# Add to existing Tallies object and re-export
tallies.append(instance_tally)
tallies.export_to_xml()

openmc.run(output=False)

with openmc.StatePoint('statepoint.25.h5') as sp:
    t = sp.tallies[2]
    flux_inst = t.mean.ravel()
    
    df = t.get_pandas_dataframe()
    print(df)

instance = df['cellinstance']['instance']
instance_to_index = dict(zip(instance.values, instance.index))
pprint(instance_to_index, width=1)

img[:] = np.nan
with openmc.lib.run_in_memory():
    for row, y in enumerate(np.linspace(ymin, ymax, resolution[0])):
        for col, x in enumerate(np.linspace(xmin, xmax, resolution[1])):
            try:
                # For each (x, y, z) point, determine the cell and distribcell index
                cell, distribcell_index = openmc.lib.find_cell((x, y, 0.))
            except openmc.exceptions.GeometryError:
                # If a point appears outside the geometry, you'll get a GeometryError exception.
                # These lines catch the exception and assign a "null" value for the array
                continue

            if cell.id == fuel_cell.id:
                # When the cell ID matches, we set the corresponding pixel in the image using the
                # distribcell index. NOTE: In this case, we need to use the dictionary to find the
                # proper index in the flux array
                index = instance_to_index.get(distribcell_index)
                if index is not None:
                    # If the distribcell instance was specified in our filter, get the flux value
                    img[row, col] = flux_inst[index]

# Plot the image using the same options as before. Notably, this ensures that the colors are consistent.
plt.imshow(img, **options)
plt.xlabel('x [cm]')
plt.ylabel('y [cm]')
plt.colorbar()

