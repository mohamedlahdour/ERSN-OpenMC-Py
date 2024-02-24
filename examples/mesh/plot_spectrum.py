import matplotlib.pyplot as plt
import openmc


# Get results from statepoint
with openmc.StatePoint('statepoint.100.h5') as sp:
    t = sp.get_tally(name="Flux in cell")
    cell_filters = t.filters[0]
    mean = {}
    for cell_id in cell_filters.bins:
        mean[cell_id]=[]

	# Get the energies from the energy filter
        energy_filter = t.filters[1]
        energies = energy_filter.bins[:, 1]
        print(energies)


	# Get the flux values
        mean[cell_id] = t.get_values(value='mean', filters=[openmc.CellFilter, openmc.EnergyFilter],filter_bins=[(cell_id,),(energies,)]) 
        #uncertainty = t.get_values(value='std_dev').ravel()
        print(mean[cell_id])

        # Plot flux spectrum

        fix, ax = plt.subplots()
        ax.loglog(energies, mean[cell_id], drawstyle='steps-post')
        ax.set_xlabel('Energy [eV]')
        ax.set_ylabel('Flux')
        ax.grid(True, which='both')
        plt.show()

