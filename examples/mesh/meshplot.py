import numpy as np
import matplotlib.pyplot as plt
import openmc

# Get results from statepoint
with openmc.StatePoint('statepoint.100.h5') as sp:
    tally = sp.get_tally()
    #print(sp.tallies)
    #print(tally.filters)
    #print(tally.filters[0])
    print(tally.filters[0].mesh)
    print('id :', tally.filters[0].mesh.id)
    print('name :', tally.filters[0].mesh.name)
    print('dimension :', tally.filters[0].mesh.dimension)
    print('width :', tally.filters[0].mesh.width)
    print('lower_left :', tally.filters[0].mesh.lower_left)
    print('upper_right :', tally.filters[0].mesh.upper_right)
    print('n_dimension :', tally.filters[0].mesh.n_dimension)
    mesh_ids = tally.filters[0].bins
    #print([mesh_id[i] for i in range(0,len(mesh_id),10000)])
    z_id = [item[2] for item in [mesh_ids[i] for i in range(0,len(mesh_ids),12*12)]]
    print(z_id)
    #print(tuple(tally.filters[0].mesh.dimension))
    x = np.linspace(tally.filters[0].mesh.lower_left[0], tally.filters[0].mesh.upper_right[0], num=tally.filters[0].mesh.dimension[0] + 1)
    y = np.linspace(tally.filters[0].mesh.lower_left[1], tally.filters[0].mesh.upper_right[1], num=tally.filters[0].mesh.dimension[1] + 1)
    z = np.linspace(tally.filters[0].mesh.lower_left[2], tally.filters[0].mesh.upper_right[2], num=tally.filters[0].mesh.dimension[1] + 1)
    list_z = ['slice at z = ' + str("{:.1E}".format(z_)) for z_ in z]
    print(list_z)
    print(mesh_ids)
    mean = tally.get_values(scores=['flux'], value='mean', filters=[openmc.MeshFilter],
                                                filter_bins=[tuple(mesh_ids)]).ravel()

    print(mean)