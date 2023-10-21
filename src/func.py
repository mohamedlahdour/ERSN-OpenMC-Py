#!usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDesktopWidget, QMessageBox

def resize_ui(self):
    # to show window at the middle of the screen and resize it to the screen size
    qtRectangle = self.frameGeometry()
    centerPoint = QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    self.move(qtRectangle.topLeft())

    ratio = 1  # float(self.comboBox_2.currentText())
    width = int(QDesktopWidget().availableGeometry().width() * ratio)
    height = int(QDesktopWidget().availableGeometry().height() * ratio)
    self.setMaximumWidth(width)
    self.setMaximumHeight(height)

def Find_string(self, text_window, string_to_find):
    self.current_line = ""
    self.line_number = 0
    self.Insert_Header = True
    document = text_window.toPlainText()
    for line in document.split('\n'):
        self.line_number += 1
        if string_to_find in line:
            self.current_line = line
            self.Insert_Header = False

def detect_component(self, text_window, string_to_find):
    self.list_of_items = []
    lines = text_window.toPlainText().split('\n')
    print(len(lines))
    for line in lines:
        if string_to_find in line:
            self.list_of_items = line[line.find("[") + 1: line.find("]")].replace(' ', '').split(',')

def CursorPosition(self):
    line = self.plainTextEdit_7.textCursor().blockNumber() + 1
    col = self.plainTextEdit_7.textCursor().columnNumber() + 1
    linecol = ("Line: " + str(line) + " | " + "Column: " + str(col))
    self.statusbar.showMessage(linecol)

def Surf(self):
    self.editor.insertPlainText('<surface id="" type="" coeffs="" boundary=""/>\n')
def Cell(self):
    self.editor.insertPlainText('<cell id="" > \n    <material>  </material>  \n    <region>  </region> \n    <universe>  </universe>\n')
    self.editor.insertPlainText('    <fill>  </fill> \n    <rotation>  </rotation> \n    <translation>  </translation> \n </cell>\n')
def Hex_Lat(self):
    self.editor.insertPlainText('<hex_lattice id=" " n_rings=" " n_axial=" " outer=" "> \n    <center>  </center> \n    <pitch>  </pitch>\n')
    self.editor.insertPlainText('    <universes> \n    </universes> \n </hex_lattice>\n')
def Rec_Lat(self):
    self.editor.insertPlainText('<lattice id=" " dimension=" " outer=" "> \n    <lower_left>   </lower_left> \n    <pitch>  </pitch>\n')
    self.editor.insertPlainText('    <universes> \n    </universes> \n </lattice>\n')
def Comment(self):
    self.editor.insertPlainText(' <!--            -->\n')
def Mat(self):
    self.editor.insertPlainText('\n<material depletable="false" id="" name=""> \n    <density value="" units="" /> \n')
    self.editor.insertPlainText('    <nuclide name=""  wo="" /> \n    <sab name=""  /> \n </material>\n')
def Settings(self):
    if self.comboBox_3.currentIndex()==0:
        pass
    elif self.comboBox_3.currentIndex()==1:
        self.editor.insertPlainText('<confidence_intervals> false </confidence_intervals>\n')
    elif self.comboBox_3.currentIndex()==2:
        self.editor.insertPlainText('<cross_sections>  </cross_sections>\n')
    elif self.comboBox_3.currentIndex()==3:
        self.editor.insertPlainText('<cutoff> \n  <weight> 0.25 </weight> \n  <weight_avg> 1 </weight_avg> \n </cutoff>\n')
    elif self.comboBox_3.currentIndex()==4:
        self.editor.insertPlainText('<run_mode>eigenvalue</run_mode> \n    <batches> </batches> \n    <generations_per_batch>    </generations_per_batch>\n')
        self.editor.insertPlainText('    <inactive> </inactive> \n    <particles> </particles>\n')
    elif self.comboBox_3.currentIndex() == 5:
        self.editor.insertPlainText('<electron_treatment>ttb</electron_treatment>   <!-- ttb or led -->\n')
    elif self.comboBox_3.currentIndex()==6:
        self.editor.insertPlainText('<energy_grid> union </energy_grid>\n')
    elif self.comboBox_3.currentIndex()==7:
        self.editor.insertPlainText('<mesh id=""> \n    <dimension>   </dimension> \n    <lower_left>   </lower_left> \n    <upper_right>   </upper_right>\n')
        self.editor.insertPlainText('</mesh>  \n <entropy_mesh>  </entropy_mesh>\n')
    elif self.comboBox_3.currentIndex()==8:
        self.editor.insertPlainText('<run_mode>fixed source</run_mode> \n    <batches>    </batches> \n    <particles>   </particles>\n')
    elif self.comboBox_3.currentIndex()==9:
        self.editor.insertPlainText('<log_grid_bins> \n </log_grid_bins>\n')
    elif self.comboBox_3.currentIndex()==10:
        self.editor.insertPlainText('<natural_elements>   </natural_elements>\n')
    elif self.comboBox_3.currentIndex()==11:
        self.editor.insertPlainText('<no_reduce> false </no_reduce>\n')
    elif self.comboBox_3.currentIndex()==12:
        self.editor.insertPlainText('<output> \n    <cross_sections> false  </cross_sections> \n    <summary> false  </summary> \n    <tallies> false </tallies>\n')
        self.editor.insertPlainText('</output>\n')
    elif self.comboBox_3.currentIndex()==13:
        self.editor.insertPlainText('<output_path>  </output_path>\n')
    elif self.comboBox_3.currentIndex()==14:
        self.editor.insertPlainText('< photon_transport > true < /photon_transport >\n')
        self.editor.insertPlainText('< cutoff >\n')
        self.editor.insertPlainText('    < energy_photon > 1000 < /energy_photon >     <!-- 1000eV is a default -->\n')
        self.editor.insertPlainText('< /cutoff >\n')
    elif self.comboBox_3.currentIndex()==15:
        self.editor.insertPlainText('<run_mode>plot</run_mode>\n')
    elif self.comboBox_3.currentIndex()==16:
        self.editor.insertPlainText('<ptables> true </ptables>\n')
    elif self.comboBox_3.currentIndex()==17:
        self.editor.insertPlainText('<resonance_scattering> \n  <scatterer> \n    <nuclide> </nuclide> \n    <method> </method> \n    <xs_label> </xs_label>\n')
        self.editor.insertPlainText('    <xs_label_0K> </xs_label_0K> \n    <E_min> </E_min> \n    <E_max> </E_max> \n  </scatterer> \n</resonance_scattering>\n')
    elif self.comboBox_3.currentIndex()==18:
        self.editor.insertPlainText('<run_cmfd> false </run_cmfd>\n')
    elif self.comboBox_3.currentIndex()==19:
        self.editor.insertPlainText('<seed> 1 </seed>\n')
    elif self.comboBox_3.currentIndex()==20:
        self.editor.insertPlainText('<source particle="" > \n    <file>  </file> \n    <space> \n        <type> </type> \n        <parameters> </parameters>\n')
        self.editor.insertPlainText('    </space> \n    <angle> \n        <type> </type> \n        <parameters> </parameters> \n    </angle> \n    <energy>\n')
        self.editor.insertPlainText('        <type> </type> \n        <parameters> </parameters> \n    </energy> \n</source>\n')
    elif self.comboBox_3.currentIndex()==21:
        self.editor.insertPlainText('<source_point> \n  <batches>  </batches> \n  <interval>  </interval> \n  <separate>  </separate> \n  <source_write>  </source_write>\n')
        self.editor.insertPlainText('  <overwrite_latest>  </overwrite_latest> \n</source_point>\n')
    elif self.comboBox_3.currentIndex()==22:
        self.editor.insertPlainText('<state_point> \n    <batches>  </batches> \n    <interval>  </interval> \n</state_point>\n')
    elif self.comboBox_3.currentIndex()==23:
        self.editor.insertPlainText('<survival_biasing> false </survival_biasing>\n')
    elif self.comboBox_3.currentIndex()==24:
        self.editor.insertPlainText('<threads>  </threads>\n')
    elif self.comboBox_3.currentIndex()==25:
        self.editor.insertPlainText('<trace>  </trace>\n')
    elif self.comboBox_3.currentIndex()==26:
        self.editor.insertPlainText('<track> </track>\n')
    elif self.comboBox_3.currentIndex()==27:
        self.editor.insertPlainText('<trigger> \n    <active> </active> \n    <max_batches> </max_batches> \n    <batch_interval> </batch_interval> \n</trigger>\n')
    elif self.comboBox_3.currentIndex()==28:
        self.editor.insertPlainText('<uniform_fs> \n    <lower_left>   </lower_left> \n     <upper_right>   </upper_right> \n     <dimension>   </dimension> \n</uniform_fs>\n')
    elif self.comboBox_3.currentIndex()==29:
        self.editor.insertPlainText('<verbosity  value="5"/>\n')
    elif self.comboBox_3.currentIndex()==30:
        self.editor.insertPlainText('<!--            -->\n')
    self.comboBox_3.setCurrentIndex(0)

def Tally(self):
    self.editor.insertPlainText('<tally id="" > \n  <name >  </name> \n    <filters>  </filters> \n    <scores >  </scores> \n    <nuclides> </nuclides>\n')
    self.editor.insertPlainText('    <trigger> \n        <type> </type> \n        <threshold> </threshold> \n        <scores> </scores> \n    </trigger> \n</tally>\n')
def Filter(self):
    self.editor.insertPlainText('<filter id="" type="" > \n    <bins>  </bins> \n</filter>\n')
def Mesh(self):
    self.editor.insertPlainText('<mesh id=""> \n    <type>   </type> \n    <dimension>  </dimension> \n    <upper_right>   </upper_right> \n    <lower_left>   </lower_left>\n')
    self.editor.insertPlainText('     <width>  </width> \n</mesh>\n')
def Ass_Sep(self):
    self.editor.insertPlainText('<assume_separate> false </assume_separate>\n')
def CMDF(self):
    if self.comboBox_4.currentIndex()==0:
        pass
    elif self.comboBox_4.currentIndex()==1:
        self.editor.insertPlainText('<begin>  </begin>\n')
    elif self.comboBox_4.currentIndex()==2:
        self.editor.insertPlainText('<dhat_set>  </dhat_set>\n')
    elif self.comboBox_4.currentIndex()==3:
        self.editor.insertPlainText('<display> </display>\n')
    elif self.comboBox_4.currentIndex()==4:
        self.editor.insertPlainText('<downscatter>  </downscatter>\n')
    elif self.comboBox_4.currentIndex()==5:
        self.editor.insertPlainText('<feedback>  </feedback>\n')
    elif self.comboBox_4.currentIndex()==6:
        self.editor.insertPlainText('<gauss_seidel_tolerance>  </gauss_seidel_tolerance>\n')
    elif self.comboBox_4.currentIndex()==7:
        self.editor.insertPlainText('<ktol>  </ktol>\n')
    elif self.comboBox_4.currentIndex()==8:
        self.editor.insertPlainText('<mesh> \n    <dimension>  </dimension> \n    <upper_right>   </upper_right> \n    <lower_left>   </lower_left> \n    <energy>   </energy>\n')
        self.editor.insertPlainText('    <albedo>   </albedo> \n    <width>  </width> \n    <map>  </map> \n    <universes> \n\n    </universes> \n</mesh>\n')
    elif self.comboBox_4.currentIndex()==9:
        self.editor.insertPlainText('<norm>  </norm>\n')
    elif self.comboBox_4.currentIndex()==10:
        self.editor.insertPlainText('<power_monitor>  </power_monitor>\n')
    elif self.comboBox_4.currentIndex()==11:
        self.editor.insertPlainText('<run_adjoint>  </run_adjoint>\n')
    elif self.comboBox_4.currentIndex()==12:
        self.editor.insertPlainText('<shift>  </shift>\n')
    elif self.comboBox_4.currentIndex()==13:
        self.editor.insertPlainText('<spectral>  </spectral>\n')
    elif self.comboBox_4.currentIndex()==14:
        self.editor.insertPlainText('<stol>  </stol>\n')
    elif self.comboBox_4.currentIndex()==15:
        self.editor.insertPlainText('<tally_reset>  </tally_reset>\n')
    elif self.comboBox_4.currentIndex()==16:
        self.editor.insertPlainText('<write_matrices> \n\n </write_matrices>\n')
    elif self.comboBox_4.currentIndex()==17:
        self.editor.insertPlainText(' <!--            -->\n')
def Plot_S(self):
    self.editor.insertPlainText('<plot id=""  color_by=""  type="slice"  basis=""   background=""> \n     <origin>  </origin> \n     <pixels>  </pixels>\n')
    self.editor.insertPlainText('     <width>   </width> \n     <color  id=""   rgb=""/> \n     <mask   components=""   background=""/>\n')
    self.editor.insertPlainText('     <meshlines   meshtype=""  id=""   linewidth="" /> \n</plot>\n')
def Plot_V(self):
    self.editor.insertPlainText('<plot id=""  color_by=""   type="voxel"   background=""> \n    <origin>   </origin> \n    <pixels>   </pixels>\n')
    self.editor.insertPlainText('    <width>    </width> \n    <color  id=""   rgb=""/> \n    <mask components="" background=""/>\n')
    self.editor.insertPlainText('    <meshlines  meshtype=""   id=""   linewidth="" /> \n</plot>\n')

def Exit(self):
    if self.text_inserted:
        self.close()
    else:
        if str(self.plainTextEdit.toPlainText()) in ['', ' ']:
            self.close()
        else:
            qm = QMessageBox
            ret = qm.question(self, 'Warning', 'Do you really want to exit window ?', qm.Yes | qm.No)
            if ret == qm.Yes:
                #self.Clear_Lists()
                self.close()
            elif ret == qm.No:
                pass

def showDialog(self, alert, msg):
    font = QFont('Arial', 12)
    msgBox = QMessageBox()
    msgBox.setFont(font)
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText(msg)
    msgBox.setWindowTitle(alert)
    msgBox.exec()
    return

def Def_Source_ToolTips(self):
    from PyQt5 import QtCore
    '''self.groupBox.setToolTip('Once you have created the materials and geometry for your simulation, the last step to have a' +
                            '\ncomplete model is to specify execution settings through the openmc.Settings class. At a minimum,' +
                            '\nyou need to specify a source distribution and how many particles to run. Many other execution'+
                            '\nsettings can be set using the openmc.Settings object, but they are generally optional.')   '''
    self.Run_Mode_CB.setItemData(0, 'The Settings.run_mode attribute controls what run mode is used when openmc is executed.' +
                                '\nThere are five different run modes that can be specified: eigenvalue, fixed source, volum, plot and particle restart'+
                                 '\nIn this menu one can find the first three modes.' +
                                 '\nIf you don’t specify a run mode, the default run mode is ‘eigenvalue’.', QtCore.Qt.ToolTipRole)
    self.Run_Mode_CB.setItemData(1, 'Runs a k eigenvalue simulation. See Eigenvalue Calculations for a full description of eigenvalue calculations.' +
                                '\nIn this mode, the Settings.source specifies a starting source that is only used for the first fission generation.', QtCore.Qt.ToolTipRole)
    self.Run_Mode_CB.setItemData(2,'Runs a fixed-source calculation with a specified external source, specified in the Settings.source attribute.', QtCore.Qt.ToolTipRole)
    self.Run_Mode_CB.setItemData(3,'Runs a stochastic volume calculation.', QtCore.Qt.ToolTipRole)
    self.LineEdit_1.setToolTip('In general, the stochastic uncertainty in your simulation results is directly related to how many total active' +
                               '\nparticles are simulated (the product of the number of active batches, number of generations per batch, and' +
                               '\nnumber of particles). At a minimum, you should use enough active batches so that the central limit theorem' +
                               '\nis satisfied (about 30). Otherwise, reducing the overall uncertainty in your simulation by a factor of 2 will' +
                               '\nrequire using 4 times as many batches')
    self.LineEdit_2.setToolTip('A preset number of inactive batches are run before the active batches (where tallies are turned on) begin.' +
                               '\nThe number of inactive batches necessary to reach a converged source depends on the spatial extent of the ' +
                               '\nproblem, its dominance ratio, what boundary conditions are used, and many other factors. For small problems,' +
                               '\nusing 50–100 inactive batches is likely sufficient. For larger models, many hundreds of inactive batches may' +
                               '\nbe necessary. Users are recommended to use the Shannon entropy diagnostic as a way of determining how many ' +
                               '\ninactive batches are necessary.')
    self.LineEdit_5.setToolTip('The standard deviation of tally results is calculated assuming that all realizations (batches) are independent.' +
                                       '\nHowever, in a kkk eigenvalue calculation, the source sites for each batch are produced from fissions in the ' +
                                       '\npreceding batch, resulting in a correlation between successive batches. This correlation can result in an ' +
                                       '\nunderprediction of the variance. That is, the variance reported is actually less than the true variance. ' +
                                       '\nTo mitigate this effect, OpenMC allows you to group together multiple fission generations into a single batch' +
                                       '\nfor statistical purposes, rather than having each fission generation be a separate batch, which is the default behavior.')
    self.Particles_Number.setToolTip('The total number of active particles will determine the level of stochastic uncertainty in simulation results,' +
                                     '\nso using a higher number of particles will result in less uncertainty.')
    self.Create_Separate_SRC_CB.setToolTip('Check to write the source distribution separate from the normal statepoint file (that contains tally ' +
                                           '\nresults and other metadata). Then, for a second simulation, you would tell OpenMC to use the ' +
                                           '\nsource file that was written out previously with')
    self.Create_Surface_SRC_CB.setToolTip('A source file based on particles that cross one or more surfaces can be generated during a simulation' +
                                           '\nusing the Settings.surf_source_write attribute:' +
                                           "\n\nsettings.surf_source_write = {'surfaces_ids': [1, 2, 3],'max_particles': 10000 }"
                                           '\n\nIn this example, at most 10,000 source particles are stored when particles cross surfaces with IDs of 1, 2, or 3.')
    self.Photon_CB.setToolTip('In addition to neutrons, OpenMC is also capable of simulating the passage of photons through matter.'+
                     '\nThis allows the modeling of photon production from neutrons as well as pure photon calculations. ' +
                     '\nThe Settings.photon_transport attribute can be used to enable photon transport')
    self.ttb_RB.setToolTip('The way in which OpenMC handles secondary charged particles can be specified with the Settings.electron_treatment attribute.' +
                     '\nBy default, the thick-target bremsstrahlung (TTB) approximation is used to generate bremsstrahlung radiation emitted by ' +
                     '\nelectrons and positrons created in photon interactions. To neglect secondary bremsstrahlung photons and instead deposit all' +
                     '\nenergy from electrons locally, the local energy deposition option can be selected: TEL')
    self.Photon_Cut.setToolTip('Because photon interactions depend on material properties below ∼1 keV, this is typically the cutoff ' +
                     '\nenergy used in photon calculations to ensure that the free atom model remains valid.')
    self.Source_Geom_CB.setToolTip('The spatial distribution can be set equal to a sub-class of openmc.stats.Spatial;' +
                                  '\ncommon choices are openmc.stats.Point or openmc.stats.Box. To independently specify ' +
                                  '\ndistributions in the xxx, yyy, and zzz coordinates, you can use openmc.stats.CartesianIndependent.' +
                                  '\nTo independently specify distributions using spherical or cylindrical coordinates, ' +
                                  '\nyou can use openmc.stats.SphericalIndependent or openmc.stats.CylindricalIndependent, respectively.')
    self.Direction_Dist_CB.setToolTip('The angular distribution can be set equal to a sub-class of openmc.stats.UnitSphere' +
                                      '\nsuch as openmc.stats.Isotropic, openmc.stats.Monodirectional, or openmc.stats.PolarAzimuthal.'
                                      '\nBy default, if no angular distribution is specified, an isotropic angular distribution is used.'
                                      '\nAs an example of a non-trivial angular distribution, the following code would create a conical ' +
                                      '\ndistribution with an aperture of 30 degrees pointed in the positive x direction:' +
                                       '\n\nfrom math import pi, cos' +
                                      '\naperture = 30.0' +
                                      '\nmu = openmc.stats.Uniform(cos(aperture/2), 1.0)' +
                                      '\nphi = openmc.stats.Uniform(0.0, 2*pi)' +
                                      '\nangle = openmc.stats.PolarAzimuthal(mu, phi, reference_uvw=(1., 0., 0.))')
    self.Energy_Dist_CB.setToolTip('The energy distribution can be set equal to any univariate probability distribution. ' +
                                   '\nThis could be a probability mass function (openmc.stats.Discrete), a Watt fission ' +
                                   '\nspectrum (openmc.stats.Watt), or a tabular distribution (openmc.stats.Tabular). ' +
                                   '\nBy default, if no energy distribution is specified, a Watt fission spectrum ' +
                                   '\nwith aaa = 0.988 MeV and bbb = 2.249 MeV -1 is used. As an example, to create an ' +
                                   '\nisotropic, 10 MeV monoenergetic source uniformly distributed over a cube centered ' +
                                   '\nat the origin with an edge length of 10 cm, one would run:' +
                                   '\n\nsource = openmc.Source()' +
                                   '\nsource.space = openmc.stats.Box((-5, -5, -5), (5, 5, 5))' +
                                   '\nsource.angle = openmc.stats.Isotropic()' +
                                   '\nsource.energy = openmc.stats.Discrete([10.0e6], [1.0])' +
                                   '\nsettings.source = source')
    self.Source_Geom_CB.setItemData(1, 'This spatial distribution can be used for a point source where sites are emitted at a specific ' +
                                    '\nlocation given by its Cartesian coordinates. Defaults to (0., 0., 0.)', QtCore.Qt.ToolTipRole)
    self.Source_Geom_CB.setItemData(2, 'For a “box” or “fission” spatial distribution, parameters should be given as six real numbers, the' +
                                       '\nfirst three of which specify the lower-left corner of a parallelepiped and the last three of which ' +
                                       '\nspecify the upper-right corner. Source sites are sampled uniformly through that parallelepiped.', QtCore.Qt.ToolTipRole)
    self.Source_Geom_CB.setItemData(3, 'To independently specify distributions in the xxx, yyy, and zzz coordinates', QtCore.Qt.ToolTipRole)
    self.Source_Geom_CB.setItemData(4, 'To independently specify distributions using spherical coordinates', QtCore.Qt.ToolTipRole)
    self.Source_Geom_CB.setItemData(5, 'To independently specify distributions using cylindrical coordinates', QtCore.Qt.ToolTipRole)
    self.Source_Geom_CB.setItemData(6, 'OpenMC can use a pregenerated HDF5 source file by specifying the filename argument to openmc.Source:' +
                                          "\n\nsettings.source = openmc.Source(filename='source.h5')" +
                                          '\n\nStatepoint and source files are generated automatically when a simulation is run and can be used ' +
                                          '\nas the starting source in a new simulation. Alternatively, a source file can be manually generated ' +
                                          '\nwith the openmc.write_source_file() function. This is particularly useful for coupling OpenMC with ' +
                                          '\nanother program that generates a source to be used in OpenMC.', QtCore.Qt.ToolTipRole)
    self.Array_Sources_RB.setToolTip('Create an array of different sources; for example:' +
                                     '\n\nsource1 = openmc.Source(spatial1, angle1, energy1, strength=0.5)' +
                                     '\nsource2 = openmc.Source(spatial2, angle2, energy2, strength=0.3)' +
                                     '\nsource3 = openmc.Source(spatial3, angle3, energy3, strength=0.1)' +
                                     '\nsource4 = openmc.Source(spatial4, angle3, energy3, strength=0.1)' +
                                     '\nsource5 = openmc.Source(spatial5, angle3, energy3, strength=0.1)' +
                                     '\n\nsettings.source = [source1, source2, source3, source4, source5]')
    for combobox in [self.X_Dist_CB, self.Y_Dist_CB, self.Z_Dist_CB]:
        combobox.setItemData(0,'Create an initial uniform spatial source distribution', QtCore.Qt.ToolTipRole)
    if self.Source_Geom_CB.currentIndex() == 0:                             # box source
        for LineEdit in [self.X_LL, self.Y_LL, self.Z_LL, self.X_UR, self.Y_UR, self.Z_UR]:
            LineEdit.setToolTip('Chose source type first')
    elif self.Source_Geom_CB.currentIndex() == 1:                           # point source
        self.X_LL.setToolTip('Enter X coordinate of point source')
        self.Y_LL.setToolTip('Enter Y coordinate of point source')
        self.Z_LL.setToolTip('Enter Z coordinate of point source')
        self.X_UR.setToolTip('')
        self.Y_UR.setToolTip('')
        self.Z_UR.setToolTip('')
    elif self.Source_Geom_CB.currentIndex() == 2:                           # box source
        self.X_LL.setToolTip('Enter Lower Left X coordinate of Box source')
        self.Y_LL.setToolTip('Enter Lower Left Y coordinate of Box source')
        self.Z_LL.setToolTip('Enter Lower Left Z coordinate of Box source')
        self.X_UR.setToolTip('Enter Upper Right X coordinate of Box source')
        self.Y_UR.setToolTip('Enter Upper Right Y coordinate of Box source')
        self.Z_UR.setToolTip('Enter Upper Right Z coordinate of Box source')
    elif self.Source_Geom_CB.currentIndex() == 3:                           # Cartesian Independent
        if self.X_Dist_CB.currentIndex() == 0:                                  # uniform
            self.X_LL.setToolTip('Enter min value')
            self.X_UR.setToolTip('Enter max value')
        if self.Y_Dist_CB.currentIndex() == 0:                                  # uniform
            self.Y_LL.setToolTip('Enter min value')
            self.Y_UR.setToolTip('Enter max value')
        if self.Z_Dist_CB.currentIndex() == 0:                                  # uniform
            self.Z_LL.setToolTip('Enter min value')
            self.Z_UR.setToolTip('Enter max value')
        if self.X_Dist_CB.currentIndex() == 1:                                  # discrete
            self.X_LL.setToolTip('Enter a list of X values, separated by comma')
            self.X_UR.setToolTip('Enter a list of corresponding probabilities')
        if self.Y_Dist_CB.currentIndex() == 1:                                  # discrete
            self.Y_LL.setToolTip('Enter a list of Y values, separated by comma')
            self.Y_UR.setToolTip('Enter a list of corresponding probabilities')
        if self.Z_Dist_CB.currentIndex() == 1:                                  # discrete
            self.Z_LL.setToolTip('Enter a list of Z values, separated by comma')
            self.Z_UR.setToolTip('Enter a list of corresponding probabilities')
        if self.X_Dist_CB.currentIndex() == 2:                                  # tabular
            self.X_LL.setToolTip('Enter a list of X values, separated by comma')
            self.X_UR.setToolTip('Enter a list of corresponding probabilities')
        if self.Y_Dist_CB.currentIndex() == 2:                                  # tabular
            self.Y_LL.setToolTip('Enter a list of Y values, separated by comma')
            self.Y_UR.setToolTip('Enter a list of corresponding probabilities')
    if self.Z_Dist_CB.currentIndex() == 2:                                  # tabular
        self.Z_LL.setToolTip('Enter a list of Z values, separated by comma')
        self.Z_UR.setToolTip('Enter a list of corresponding probabilities')
    elif self.Source_Geom_CB.currentIndex() == 4:                       # Spherical Independent
        if self.X_Dist_CB.currentIndex() == 0:                              # uniform
            self.X_LL.setToolTip('Enter min value')
            self.X_UR.setToolTip('Enter max value')
        if self.Y_Dist_CB.currentIndex() == 0:                              # uniform
            self.Y_LL.setToolTip('Enter min value: 0.0')
            self.Y_UR.setToolTip('Enter max value: pi')
        if self.Z_Dist_CB.currentIndex() == 0:                              # uniform
            self.Z_LL.setToolTip('Enter min value: 0.0')
            self.Z_UR.setToolTip('Enter max value: 2*pi')
        if self.X_Dist_CB.currentIndex() == 1:                              # discrete
            self.X_LL.setToolTip('Enter a list of R values, separated by comma: R1, R2, R3')
            self.X_UR.setToolTip('Enter a list of corresponding probabilities: P1, P2, P3')
        if self.Y_Dist_CB.currentIndex() == 1:                              # discrete
            self.Y_LL.setToolTip('Enter a list of Theta values, separated by comma: pi/4, pi/2, pi')
            self.Y_UR.setToolTip('Enter a list of corresponding probabilities: 0.3, 0.4, 0.3')
        if self.Z_Dist_CB.currentIndex() == 1:                              # discrete
            self.Z_LL.setToolTip('Enter a list of Phi values, separated by comma: 0.0, pi, 2*pi')
            self.Z_UR.setToolTip('Enter a list of corresponding probabilities: 0.2, 0.4, 0.3')
        self.Origin_LE.setToolTip('Enter coordinates of spherical source: [0.0, 0.0, 0.0]')
    elif self.Source_Geom_CB.currentIndex() == 5:                       # Cylindrical Independent
        if self.X_Dist_CB.currentIndex() == 0:                              # uniform
            self.X_LL.setToolTip('Enter min value')
            self.X_UR.setToolTip('Enter max value')
        if self.Y_Dist_CB.currentIndex() == 0:                              # uniform
            self.Y_LL.setToolTip('Enter min value: 0.0')
            self.Y_UR.setToolTip('Enter max value: 2.*pi')
        if self.Z_Dist_CB.currentIndex() == 0:                              # uniform
            self.Z_LL.setToolTip('Enter min value')
            self.Z_UR.setToolTip('Enter max value')
        if self.X_Dist_CB.currentIndex() == 1:                              # discrete
            self.X_LL.setToolTip('Enter a list of R values, separated by comma: R1, R2, R3')
            self.X_UR.setToolTip('Enter a list of corresponding probabilities: P1, P2, P3')
        if self.Y_Dist_CB.currentIndex() == 1:                              # discrete
            self.Y_LL.setToolTip('Enter a list of Phi values, separated by comma: 0.0, pi, 2.0*pi')
            self.Y_UR.setToolTip('Enter a list of corresponding probabilities: [0.3, 0.4, 0.3]')
        if self.Z_Dist_CB.currentIndex() == 1:                              # discrete
            self.Z_LL.setToolTip('Enter a list of Z values, separated by comma')
            self.Z_UR.setToolTip('Enter a list of corresponding probabilities')
        self.Origin_LE.setToolTip('Enter coordinates of cylindrical source: 0.0, 0.0, 0.0')
    self.Source_GB.setToolTip(
            'The openmc.Source class has three main attributes that one can set: Source.space, ' +
            '\nwhich defines the spatial distribution, Source.angle, which defines the angular distribution,' +
            ' \n and Source.energy, which defines the energy distribution.')
    self.Energy_Dist_CB.setItemData(1, 'Distribution characterized by a probability mass function', QtCore.Qt.ToolTipRole)
    self.Energy_Dist_CB.setItemData(2, 'Maxwellian distribution in energy', QtCore.Qt.ToolTipRole)
    self.Energy_Dist_CB.setItemData(3, 'Watt fission energy spectrum', QtCore.Qt.ToolTipRole)
    self.Energy_Dist_CB.setItemData(4, 'Piecewise continuous probability distribution', QtCore.Qt.ToolTipRole)
    self.Direction_Dist_CB.setItemData(1, 'Isotropic angular distribution', QtCore.Qt.ToolTipRole)
    self.Direction_Dist_CB.setItemData(2, 'Monodirectional angular distribution', QtCore.Qt.ToolTipRole)
    self.Direction_Dist_CB.setItemData(3, 'Distribution of points on the unit sphere', QtCore.Qt.ToolTipRole)
    self.Direction_Dist_CB.setItemData(4, 'Angular distribution represented by polar and azimuthal angles', QtCore.Qt.ToolTipRole)
    if self.Energy_Dist_CB.currentIndex() == 1:
        self.Energy_LE.setToolTip('Enter Energy or list of Energies in eV separated by blank, comma or semicolon : 0.025 0.1E3 20E6')
        self.Proba_LE.setToolTip('Enter Probability or list of Probabilities separated by blank, comma or semicolon : 0.5 0.2 0.3')
    if self.Energy_Dist_CB.currentIndex() == 2:
        self.Energy_LE.setToolTip('Enter the temperature parameter of Maxwellian spectrum in eV')
        self.Proba_LE.setToolTip(None)
    if self.Energy_Dist_CB.currentIndex() == 3:
        self.Energy_LE.setToolTip('Enter the a parameter of Watt spectrum in eV')
        self.Proba_LE.setToolTip('Enter the b parameter of Watt spectrum in 1/eV')
    if self.Energy_Dist_CB.currentIndex() == 4:
        self.Energy_LE.setToolTip('Enter the list of energies in eV separated by blank, comma or semicolon for interpolation')
        self.Proba_LE.setToolTip('Enter the list of Probabilities per eV separated by blank, comma or semicolon for interpolation')

    if self.Direction_Dist_CB.currentIndex() == 1:
        self.Energy_LE.setToolTip(None)
        self.Proba_LE.setToolTip(None)
    if self.Direction_Dist_CB.currentIndex() == 2:
        self.Energy_LE.setToolTip('Enter the temperature parameter of Maxwellian spectrum in eV')
        self.Proba_LE.setToolTip(None)
    if self.Direction_Dist_CB.currentIndex() == 3:
        self.Energy_LE.setToolTip('Enter the a parameter of Watt spectrum in eV')
        self.Proba_LE.setToolTip('Enter the b parameter of Watt spectrum in 1/eV')
    if self.Direction_Dist_CB.currentIndex() == 4:
        self.Energy_LE.setToolTip('Enter the list of energies in eV separated by blank, comma or semicolon for interpolation')
        self.Proba_LE.setToolTip('Enter the list of Probabilities per eV separated by blank, comma or semicolon for interpolation')
    self.Exit_PB.setToolTip('Exit this window')
    self.Clear_PB.setToolTip('Clear the output window')
    self.Export_Settings_PB.setToolTip('Export edited data to the main editing window of the project python model')
    for buttons in [self.Add_Run_Mode_PB, self.Add_Vol_Calc_PB, self.Add_Entropy_PB, self.Add_Source_PB]:
        buttons.setToolTip('Click to send data to to the Output text window')
    if self.Source_Geom_CB.currentIndex() in [1, 4]:
        self.Import_Lists_PB.setToolTip('Import Energies and Probabilities from text file. Data must be arranged in two columns !')
   
