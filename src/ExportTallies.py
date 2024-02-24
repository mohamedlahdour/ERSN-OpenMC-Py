# -*- coding: utf-8 -*-
import sys
import string
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from src.syntax_py import Highlighter
from src.PyEdit import TextEdit, NumberBar  

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self,text):
        self.textWritten.emit(str(text))
        pass

    def flush(self):
        pass 

class ExportTallies(QWidget):
    from .func import resize_ui, showDialog, Exit
    def __init__(self,v_1, available_xs, Tally, Tally_ID, Filter, Filter_ID, Scores, Scores_ID, Surf_list, Surf_Id_list, Cells_list,
                 Cell_Id_list, univ, mat, elements, nuclides, mesh, mesh_ID, parent=None):
        super(ExportTallies, self).__init__(parent)
        #sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        v_1.moveCursor(QtGui.QTextCursor.End)
        uic.loadUi("src/ui/ExportTally.ui", self)
        self.v_1 = v_1
        self._initButtons()

        # validators
        self.Set_Validators()
        
        self.Mesh_LE_1.setToolTip("Only integers separated by ,;: are accepted")
        for item in [self.TallyId_LE, self.FilterId_LE, self.MeshId_LE, self.GrpNumber_LE]:
            item.setValidator(self.int_validator)
            item.setToolTip("Only integer is accepted")

        for LineEd in [self.Start_LE, self.End_LE]:
            LineEd.setValidator(self.validator)
            LineEd.setToolTip("Only float number is accepted")


        for LineEd in [self.Mesh_LE_2, self.Mesh_LE_3]:
            LineEd.setValidator(self.float_validator_list)
            LineEd.setToolTip("Only float numbers separated by ,;: are accepted")

        self.tally = ''
        self.available_xs = available_xs
        self.Neutron_XS_List = self.available_xs[0]
        self.TSL_XS_List = self.available_xs[1]
        self.Photon_XS_List = self.available_xs[2]

        self.tally_name_list = Tally
        self.tally_id_list = Tally_ID
        self.filter_name_list = Filter
        self.filter_id_list = Filter_ID
        self.score_name_list = Scores
        self.score_id_list = Scores_ID
        self.surface_name_list = Surf_list
        self.surface_id_list = Surf_Id_list
        self.cell_name_list = Cells_list
        self.cell_id_list = Cell_Id_list
        self.mesh_name_list = mesh
        self.mesh_id_list = mesh_ID
        self.Filter_Bins_CB.setEnabled(False)
        self.text_inserted = False

        self.list_of_cells = []
        self.list_of_surfaces = []
        self.list_of_surfaces_ids = []
        self.universe_name_list = univ
        self.materials_name_list = mat
        self.Model_Elements_List = [elm for elm in elements]
        self.Model_Nuclides_List = [nucl for nucl in nuclides]
        self.Filter_Bins_List = []
        self.Filters_List = []
        self.Nuclides_Bins_List = []
        self.Scores_List = []
        self.tally_suffix = '_tally'
        self.old_suffix = self.Tally_LE.text().rstrip(string.digits)
        self.title = ''
        self.filter_suffix = '_filter'
        self.mesh_suffix = 'mesh'

        if len(Tally) > 0:
            self.Tally_ID = self.tally_id_list[-1] + 1
        else:
            self.Tally_ID = 1
        self.TallyId_LE.setText(str(self.Tally_ID))
        self.TallyName_LE.clear()        

        if len(mesh) > 0:
            self.Mesh_ID = self.mesh_id_list[-1] + 1
        else:
            self.Mesh_ID = 1
        self.MeshId_LE.setText(str(self.Mesh_ID))   

        if len(Filter) > 0:
            self.Filter_ID = self.filter_id_list[-1] + 1
        else:
            self.Filter_ID = 1
        self.FilterId_LE.setText(str(self.Filter_ID))
        self.Use_AllItems = False

        self.Nuclides_CB.clear()
        self.Create_New_Tally = False

        # define diffrent estimators, filters, meshes, scores, ..
        self.Inicialize_Tallies()

        for item in [self.Grid_RB, self.MinMax_RB, self.Grid_RB_2, self.MinMax_RB_2, self.Grid_RB_3, self.MinMax_RB_3, 
                     self.MGX_CB, self.label, self.label_8, self.label_10, self.Start_LE, self.End_LE, self.GrpNumber_LE]:
            item.hide()

        # add new editor
        self.plainTextEdit = TextEdit()
        self.plainTextEdit.setWordWrapMode(QTextOption.NoWrap)
        self.numbers = NumberBar(self.plainTextEdit)
        layoutH = QHBoxLayout()
        #layoutH.setSpacing(1.5)
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.plainTextEdit)
        self.EditorLayout.addLayout(layoutH, 0, 0)
        
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        # sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        # to show window at the middle of the screen and resize it to the screen size
        self.resize_ui()

    def _initButtons(self):
        self.AddTally_PB.clicked.connect(self.Add_Tallies)
        self.CreateMesh_PB.clicked.connect(self.Create_Mesh)
        self.MeshType_CB.currentIndexChanged.connect(self.Def_Mesh)
        self.CreateFilter_PB.clicked.connect(self.Create_Filters)
        self.Filter_Bins_CB.currentIndexChanged.connect(self.Show_Hide_Widgets)
        self.MGX_CB.currentIndexChanged.connect(self.Show_Hide_Widgets_1)
        self.MGX_CB.currentIndexChanged.connect(self.Choose_MGX_STR)
        self.TallyId_LE.textChanged.connect(self.sync_id)
        self.AddTallyId_CB.stateChanged.connect(self.sync_id)
        self.Tally_LE.textChanged.connect(self.sync_name)

        self.FilterId_LE.textChanged.connect(self.sync_filter_id)
        self.AddFilterId_CB.stateChanged.connect(self.sync_filter_id)
        self.FilterName_LE.textChanged.connect(self.sync_filter_name)

        self.MeshId_LE.textChanged.connect(self.sync_mesh_id)
        self.AddMeshId_CB.stateChanged.connect(self.sync_mesh_id)
        self.MeshName_LE.textChanged.connect(self.sync_mesh_name)

        self.FilterType_CB.currentIndexChanged.connect(self.Update_Filters)
        self.Filter_Bins_CB.currentIndexChanged.connect(self.Update_Filter_Bins)

        self.Filters_List_CB.currentIndexChanged.connect(self.Def_Filters_Bins_To_Tally)
        self.Nuclides_CB.currentIndexChanged.connect(self.Add_Nuclides_Bins_To_Tally)
        self.FluxScores_CB.currentIndexChanged.connect(self.DEF_FluxScores)
        self.RxnRates_CB.currentIndexChanged.connect(self.DEF_RxnRates)
        self.PartProduction_CB.currentIndexChanged.connect(self.DEF_PartProduction)
        self.MiscScores_CB.currentIndexChanged.connect(self.DEF_MiscScores)

        self.Undo_PB.clicked.connect(lambda: self.Undo(self.Filter_Bins_List, self.Filter_Bins_List_LE))
        self.Reset_PB.clicked.connect(lambda: self.Reset(self.Filter_Bins_List, self.Filter_Bins_List_LE))

        self.UndoFilter_PB.clicked.connect(lambda: self.Undo(self.Filters_List, self.Filters_List_LE))
        self.ResetFilter_PB.clicked.connect(lambda: self.Reset(self.Filters_List, self.Filters_List_LE))

        self.UndoNucl_PB.clicked.connect(lambda: self.Undo(self.Nuclides_Bins_List, self.Nuclides_Bins_List_LE))
        self.ResetNucl_PB.clicked.connect(lambda: self.Reset(self.Nuclides_Bins_List, self.Nuclides_Bins_List_LE))

        self.UndoScores_PB.clicked.connect(lambda: self.Undo(self.Scores_List, self.ScoresList_LE))
        self.ResetScores_PB.clicked.connect(lambda: self.Reset(self.Scores_List, self.ScoresList_LE))

        self.AddFilters_PB.clicked.connect(self.Add_Filters_Bins_To_Tally)
        self.AddNuclides_PB.clicked.connect(self.Add_Nuclides)
        self.AddScore_PB.clicked.connect(self.Add_Scores)

        self.ExportData_PB.clicked.connect(self.Export_Tallies)
        self.ClearData_PB.clicked.connect(self.clear_text)
        self.Exit_PB.clicked.connect(self.Exit)
        
    def Set_Validators(self):
        self.int_validator = QRegExpValidator(QRegExp(r'[0-9]+'))
        self.dim_validator = QRegExpValidator(QRegExp(r'[0-9 ,;:]+'))
        self.validator = QRegExpValidator(QRegExp("(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)"))   
        self.validator_positif = QRegExpValidator(QRegExp("((\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)"))   
        float_regexp_list = r"(([+-]?\d+(\.\d*)?|\.\d+)(([ ,;:])|[eE][+-]?\d+)([ ,;:])?)"
        regexp_list = "(float)?( +float)* *".replace("float", float_regexp_list)     
        self.float_validator_list = QRegExpValidator(QRegExp(regexp_list))
        float_regexp_list_positif = r"((\d+(\.\d*)?|\.\d+)(([ ,;:])|[eE][+-]?\d+)([ ,;:])?)"
        regexp_list_positif = "(float)?( +float)* *".replace("float", float_regexp_list_positif)
        self.float_validator_list_positif = QRegExpValidator(QRegExp(regexp_list_positif))    
        float_regexp_list_pi = r"(([+-]?\d+(\.\d*)?|[-][p][i]?|[p][i]?|\.\d+)(([ ,;:])|[eE][+-]?\d+|[*][p][i]?)(([*][p][i]?)|[ ,;:])?)"
        regexp_list_pi = "(float)?( +float)* *".replace("float", float_regexp_list_pi)     
        self.float_validator_list_pi = QRegExpValidator(QRegExp(regexp_list_pi))
        float_regexp_list_pi_positif = r"((\d+(\.\d*)?|[p][i]?|\.\d+)(([ ,;:])|[eE][+-]?\d+|[*][p][i]?)(([*][p][i]?)|[ ,;:])?)"
        regexp_list_pi_positif = "(float)?( +float)* *".replace("float", float_regexp_list_pi_positif)     
        self.float_validator_list_pi_positif = QRegExpValidator(QRegExp(regexp_list_pi_positif))
        #float_regexp_pi_positif = r"((\d+(\.\d*)?|[p][i]?|\.\d+)([eE][+-]?\d+|[*][p][i]?)(([*][p][i]?))?)"
        #regexp__pi_positif = "(float)?( +float)* *".replace("float", float_regexp_pi_positif)     
        self.float_validator_pi = QRegExpValidator(QRegExp("(([+-]?\d+(\.\d*)?|[-][p][i]?|[p][i]?|\.\d+)([eE][+-]?\d+|[*][p][i]?)(([*][p][i]?))?)"))
        self.float_validator_pi_positif = QRegExpValidator(QRegExp("((\d+(\.\d*)?|[p][i]?|\.\d+)([eE][+-]?\d+|[*][p][i]?)(([*][p][i]?))?)"))

    def Define_Tips(self):
        # define Tips of each button  
        self.FluxScores_CB.setToolTip('Flux scores: Total flux, units are particle-cm per source particle.')
        self.FluxScores_CB.setItemData(1,'Total Flux.', QtCore.Qt.ToolTipRole)
        self.MiscScores_CB.setToolTip('Miscellaneous scores: units are indicated for each.')
        self.MiscScores_CB.setItemData(1,'Used in combination with a meshsurface filter: Partial currents ' +
                                         'on the boundaries of each cell in a mesh. It may not be used in ' +
                                         'conjunction with any other score. Only energy and mesh filters may ' +
                                         'be used. Used in combination with a surface filter: Net currents on ' +
                                         'any surface previously defined in the geometry. It may be used along ' +
                                         'with any other filter, except meshsurface filters. Surfaces can ' +
                                         'alternatively be defined with cell from and cell filters thereby ' +
                                         'resulting in tallying partial currents. Units are particles per source particle.', QtCore.Qt.ToolTipRole)
        self.MiscScores_CB.setItemData(2,'Number of scoring events. Units are events per source particle.', QtCore.Qt.ToolTipRole)
        self.MiscScores_CB.setItemData(3,'The flux-weighted inverse velocity where the velocity is in units of centimeters per second.', QtCore.Qt.ToolTipRole)
        self.MiscScores_CB.setItemData(4,'Total nuclear heating in units of eV per source particle. For neutrons, ' +
                                         'this corresponds to MT=301 produced by NJOY’s HEATR module while for photons, ' +
                                         'this is tallied from direct photon energy deposition. See Heating and Energy Deposition.', QtCore.Qt.ToolTipRole)
        self.MiscScores_CB.setItemData(5,'Total nuclear heating in units of eV per source particle assuming energy from secondary ' +
                                         'photons is deposited locally. Note that this score should only be used for incident neutrons.'+
                                         'See Heating and Energy Deposition.', QtCore.Qt.ToolTipRole)
        self.MiscScores_CB.setItemData(6,'The recoverable energy production rate due to fission. The recoverable energy is defined as ' +
                                         'the fission product kinetic energy, prompt and delayed neutron kinetic energies, prompt and delayed '+
                                         'gamma-ray total energies, and the total energy released by the delayed beta particles. The neutrino '+
                                         'energy does not contribute to this response. The prompt and delayed gamma-rays are assumed to deposit '+
                                         'their energy locally. Units are eV per source particle.', QtCore.Qt.ToolTipRole)
        self.MiscScores_CB.setItemData(7,'The prompt fission energy production rate. This energy comes in the form of fission fragment nuclei,'+
                                         'prompt neutrons, and prompt gamma-rays. This value depends on the incident energy and it requires that'+
                                         'the nuclear data library contains the optional fission energy release data. Energy is assumed to be '+
                                         'deposited locally. Units are eV per source particle.', QtCore.Qt.ToolTipRole)
        self.MiscScores_CB.setItemData(8,'The recoverable fission energy production rate. This energy comes in the form of fission fragment nuclei, '+
                                         'prompt and delayed neutrons, prompt and delayed gamma-rays, and delayed beta-rays. This tally differs from '+
                                         'the kappa-fission tally in that it is dependent on incident neutron energy and it requires that the nuclear '+
                                         'data library contains the optional fission energy release data. Energy is assumed to be deposited locally. '+
                                         'Units are eV per source paticle.', QtCore.Qt.ToolTipRole)
        self.MiscScores_CB.setItemData(9,'The delayed-nu-fission-weighted decay rate where the decay rate is in units of inverse seconds.', QtCore.Qt.ToolTipRole)
        self.MiscScores_CB.setItemData(10,'Damage energy production in units of eV per source particle. This corresponds to MT=444 produced by NJOY’s HEATR module.', QtCore.Qt.ToolTipRole)

    def Inicialize_Tallies(self):       
        # define diffrent estimators, filters, meshes, scores, ...
        ESTIMATOR_TYPES = ['tracklength', 'collision', 'analog']
        self.Estimator_CB.addItems(ESTIMATOR_TYPES)
        self.PARTICLE_TYPE = ['neutron', 'photon', 'electron', 'positron']
        # Possible filters
        FILTER_TYPES = ['UniverseFilter', 'MaterialFilter', 'CellFilter', 'CellFromFilter', 'CellbornFilter',
                        'CellInstanceFilter', 'CollisionFilter', 'SurfaceFilter', 'MeshFilter', 'MeshSurfaceFilter',
                        'EnergyFilter', 'EnergyoutFilter', 'MuFilter', 'PolarFilter', 'AzimuthalFilter',
                        'DistribcellFilter', 'DelayedGroupFilter', 'EnergyFunctionFilter', 'LegendreFilter',
                        'SpatialLegendreFilter', 'SphericalHarmonicsFilter', 'ZernikeFilter', 'ZernikeRadialFilter',
                        'ParticleFilter', 'TimeFilter']
        # Possible meshes
        MESH_TYPES = ['RegularMesh', 'RectilinearMesh', 'CylindricalMesh', 'SphericalMesh', 'UnstructuredMesh']
        # Possible scores
        self.FlUX_SCORES = ['flux']
        self.REACTION_SCORES = ['absorption', 'elastic', 'fission', 'scatter', 'total', '(n,2nd)', '(n,2n)', '(n,3n)',
                                '(n,na)', '(n,n3a)', '(n,2na)', '(n,3na)', '(n,np)', '(n,n2a)', '(n,2n2a)', '(n,nd)',
                                '(n,nt)', '(n,n3He)', '(n,nd2a)', '(n,nt2a)', '(n,4n)', '(n,2np)', '(n,3np)', '(n,n2p)',
                                '(n,n*X*)', '(n,nc)', '(n,gamma)', '(n,p)', '(n,d)', '(n,t)', '(n,3He)', '(n,a)',
                                '(n,2a)', '(n,3a)', '(n,2p)', '(n,pa)', '(n,t2a)', '(n,d2a)', '(n,pd)', '(n,pt)', '(n,da)',
                                'coherent-scatter', 'incoherent-scatter', 'photoelectric', 'pair-production', 'Arbitrary integer']
        self.PARTICLE_PRODUCTION_SCORES = ['delayed-nu-fission', 'prompt-nu-fission', 'nu-fission', 'nu-scatter',
                                           'H1-production', 'H2-production', 'H3-production', 'He3-production', 'He4-production']
        self.MISCELLANEOUS_SCORES = ['current', 'events', 'inverse-velocity', 'heating', 'heating-local', 'kappa-fission',
                                     'fission-q-prompt', 'fission-q-recoverable', 'decay-rate', 'damage-energy']

        self.FILTER_SUFFIX = ['Universe_filter', 'Material_filter', 'Cell_filter', 'CellFrom_filter', 'Cellborn_filter',
                        'CellInstance_filter', 'Collision_filter', 'Surface_filter', 'Mesh_filter', 'MeshSurface_filter',
                        'Energy_filter', 'Energyout_filter', 'Mu_filter', 'Polar_filter', 'Azimuthal_filter',
                        'Distribcell_filter', 'DelayedGroup_filter', 'EnergyFunction_filter', 'Legendre_filter',
                        'SpatialLegendre_filter', 'SphericalHarmonics_filter', 'Zernike_filter', 'ZernikeRadial_filter',
                        'Particle_filter', 'Time_filter']

        if self.AddTallyId_CB.isChecked():
            self.Tally_LE.setText(self.tally_suffix + str(self.TallyId_LE.text()))
        else:
            self.Tally_LE.setText(self.tally_suffix)
        if self.AddMeshId_CB.isChecked():
            self.MeshName_LE.setText(self.mesh_suffix + str(self.MeshId_LE.text()))
        else:
            self.MeshName_LE.setText(self.mesh_suffix)

        # instantiate bins lists of filters
        self.Availble_Filters = {'UniverseFilter': self.universe_name_list, 'MaterialFilter': self.materials_name_list,
                              'CellFilter': self.cell_name_list, 'CellFromFilter': self.cell_name_list,
                              'CellbornFilter': self.cell_name_list, 'CellInstanceFilter': self.cell_name_list,
                              'SurfaceFilter': self.surface_name_list, 'MeshFilter': self.mesh_name_list,
                              'MeshSurfaceFilter': self.mesh_name_list, 'DistribcellFilter': self.cell_name_list,
                              'CollisionFilter': [],'EnergyFilter': [], 'EnergyoutFilter': [], 'MuFilter': [],
                              'PolarFilter': [], 'AzimuthalFilter': [], 'DelayedGroupFilter': [],
                              'EnergyFunctionFilter': [], 'LegendreFilter': [], 'SpatialLegendreFilter': [],
                              'SphericalHarmonicsFilter': [], 'ZernikeFilter': [], 'ZernikeRadialFilter': [],
                              'ParticleFilter': [], 'TimeFilter': []}

        self.MGX_GROUP_STRUCTURES_LIST = ['Select Structure', 'CASMO-2', 'CASMO-4', 'CASMO-8', 'CASMO-16', 'CASMO-25', 'CASMO-40', 'VITAMIN-J-42', 'CASMO-70',
                                'XMAS-172', 'VITAMIN-J-175', 'TRIPOLI-315,', 'SHEM-361', 'CCFE-709', 'UKAEA-1102']

        # Filling Available Filters combobox
        self.FilterType_CB.addItems(FILTER_TYPES)
        # Filling Meshes combobox
        self.MeshType_CB.addItems(MESH_TYPES)
        # Filling Nuclides combobox
        if self.Model_Nuclides_List:
            self.Nuclides_CB.addItems(['Select Nuclide', 'Add all nuclides'])
            self.Nuclides_CB.addItems(self.Model_Nuclides_List)
        #print(self.Model_Nuclides_List)
        # Filling SCORES combobox
        self.FluxScores_CB.addItems(self.FlUX_SCORES)
        self.RxnRates_CB.addItems(self.REACTION_SCORES)
        self.PartProduction_CB.addItems(self.PARTICLE_PRODUCTION_SCORES)
        self.MiscScores_CB.addItems(self.MISCELLANEOUS_SCORES)
        # add tips to scores
        self.Define_Tips()

        self.Filters_List_CB.clear()
        # Filling Filters ComboBox to add to tally
        if self.filter_name_list:
            self.Filters_List_CB.addItems(['Select Filter', 'All filters'])
            self.Filters_List_CB.addItems(self.filter_name_list)

    def sync_name(self):
        import string
        self.title = self.Tally_LE.text().rstrip(string.digits).replace(self.tally_suffix, '')

    def sync_id(self):
        import string
        if self.TallyId_LE.text():
            self.Tally_ID = int(self.TallyId_LE.text())
            if self.AddTallyId_CB.isChecked():
                self.Tally_LE.setText(self.Tally_LE.text().rstrip(string.digits) + str(self.Tally_ID))
            else:
                self.Tally_LE.setText(self.Tally_LE.text().rstrip(string.digits))

    def sync_filter_name(self):
        import string
        self.filter_suffix = self.FilterName_LE.text().rstrip(string.digits)

    def sync_filter_id(self):
        import string
        if self.FilterId_LE.text():
            self.Filter_ID = int(self.FilterId_LE.text())
            if self.AddFilterId_CB.isChecked():
                self.FilterName_LE.setText(self.filter_suffix + str(self.Filter_ID))
                self.filter_suffix = self.FilterName_LE.text().rstrip(string.digits)
            else:
                self.filter_suffix = self.FilterName_LE.text().rstrip(string.digits)
                self.FilterName_LE.setText(self.filter_suffix)

    def sync_mesh_name(self):
        import string
        self.mesh_suffix = self.MeshName_LE.text().rstrip(string.digits)

    def sync_mesh_id(self):
        import string
        if self.MeshId_LE.text():
            self.Mesh_ID = int(self.MeshId_LE.text())
            if self.AddMeshId_CB.isChecked():
                self.MeshName_LE.setText(self.mesh_suffix + str(self.Mesh_ID))
                self.mesh_suffix = self.MeshName_LE.text().rstrip(string.digits)
            else:
                self.mesh_suffix = self.MeshName_LE.text().rstrip(string.digits)
                self.MeshName_LE.setText(self.mesh_suffix)

    def Add_Tallies(self):
        self.Create_New_Tally = True
        self.Def_Tallies()
        if self.Tally_LE.text() == '':
            self.showDialog('Warning', 'Cannot create tally, enter name first !')
            return
        elif self.TallyId_LE.text() == '':
            self.showDialog('Warning', 'Cannot create tally, enter tally id first !')
            return
        else:
            if self.TallyName_LE.text() == '':
                self.showDialog('Warning', 'No title specification entered !')
            if self.Tally_LE.text() in self.tally_name_list:
                self.showDialog('Warning', 'Tally name already used, enter new name !')
                return
            elif int(self.TallyId_LE.text()) in self.tally_id_list:
                self.showDialog('Warning', 'Tally id already used, enter new id !')
                return
            else:
                if self.TallyName_LE.text():
                    print('\n' + self.Tally_LE.text() + ' = openmc.Tally(tally_id=' + self.TallyId_LE.text() + ", name='" + self.TallyName_LE.text() + "')")
                else:
                    print('\n' + self.Tally_LE.text() + ' = openmc.Tally(tally_id=' + self.TallyId_LE.text() + ", name='" + self.title + "')")

        self.tally = self.Tally_LE.text()
        if self.tally not in self.tally_name_list:
            self.tally_name_list.append(self.tally)
            self.tally_id_list.append(self.TallyId_LE.text())
        self.tally_suffix = '_tally'
        self.TallyName_LE.clear()
        self.tally_id = int(self.tally_id_list[-1]) + 1
        self.TallyId_LE.setText(str(self.tally_id))
        if self.AddTallyId_CB.isChecked():
            self.Tally_LE.setText(self.tally_suffix + str(self.TallyId_LE.text()))
        else:
            self.Tally_LE.setText(self.tally_suffix)

    def Def_Mesh(self):
        if self.MeshType_CB.currentIndex() == 0:
            for radio in [self.Grid_RB, self.MinMax_RB, self.Grid_RB_2, self.MinMax_RB_2, self.Grid_RB_3, self.MinMax_RB_3]:
                radio.hide()
            self.MinMax_RB.hide()
        elif self.MeshType_CB.currentIndex() == 1:                  # RegularMesh
            self.Mesh_1D.setEnabled(True)
            self.Mesh_2D.setEnabled(True)
            self.Mesh_3D.setEnabled(True)
            self.Mesh_1D.setChecked(True)
            self.Mesh_3D.setChecked(False)
            for radio in [self.Grid_RB, self.MinMax_RB, self.Grid_RB_2, self.MinMax_RB_2, self.Grid_RB_3, self.MinMax_RB_3]:
                radio.hide()
            self.label_2.setText('Dimensions')
            self.label_3.setText('Lower Left (x,y,z)')
            self.label_4.setText('Upper Right (x,y,z)')
            self.Mesh_LE_1.setValidator(self.dim_validator)
            self.Mesh_LE_2.setValidator(self.float_validator_list)
            self.Mesh_LE_3.setValidator(self.float_validator_list)
        elif self.MeshType_CB.currentIndex() == 2:                  # RectiLinearMesh
            self.Mesh_1D.setEnabled(False)
            self.Mesh_2D.setEnabled(False)
            self.Mesh_3D.setEnabled(True)
            self.Mesh_1D.setChecked(False)
            self.Mesh_3D.setChecked(True)
            for radio in [self.Grid_RB, self.MinMax_RB, self.Grid_RB_2, self.MinMax_RB_2, self.Grid_RB_3, self.MinMax_RB_3]:
                radio.show()
            self.label_2.setText('x_grid (min, max, dim)')
            self.label_3.setText('y_grid (min, max, dim)')
            self.label_4.setText('z_grid (min, max, dim)')
            self.Mesh_LE_1.setValidator(self.float_validator_list)
            self.Mesh_LE_2.setValidator(self.float_validator_list)
            self.Mesh_LE_3.setValidator(self.float_validator_list)
        elif self.MeshType_CB.currentIndex() == 3:                     # CylindricalMesh
            self.Mesh_1D.setEnabled(False)
            self.Mesh_2D.setEnabled(False)
            self.Mesh_3D.setEnabled(True)
            self.Mesh_1D.setChecked(False)
            self.Mesh_3D.setChecked(True)
            for radio in [self.Grid_RB, self.MinMax_RB, self.Grid_RB_2, self.MinMax_RB_2, self.Grid_RB_3, self.MinMax_RB_3]:
                radio.show()
            self.label_2.setText('r_grid (min, max, dim)')
            self.label_3.setText('phi_grid (min, max, dim)')
            self.label_4.setText('z_grid (min, max, dim)')
            self.Mesh_LE_1.setValidator(self.float_validator_list_positif)
            self.Mesh_LE_2.setValidator(self.float_validator_list_pi)
            self.Mesh_LE_3.setValidator(self.float_validator_list)
        elif self.MeshType_CB.currentIndex() == 4:                     # SphericalMesh
            self.Mesh_1D.setEnabled(False)
            self.Mesh_2D.setEnabled(False)
            self.Mesh_3D.setEnabled(True)
            self.Mesh_1D.setChecked(False)
            self.Mesh_3D.setChecked(True)
            for radio in [self.Grid_RB, self.MinMax_RB, self.Grid_RB_2, self.MinMax_RB_2, self.Grid_RB_3, self.MinMax_RB_3]:
                radio.show()
            self.label_2.setText('r_grid (min, max, dim)')
            self.label_3.setText('theta_grid (min, max, dim)')
            self.label_4.setText('phi_grid (min, max, dim)')
            self.Mesh_LE_1.setValidator(self.float_validator_list_positif)
            self.Mesh_LE_2.setValidator(self.float_validator_list_pi)
            self.Mesh_LE_3.setValidator(self.float_validator_list_pi)
        elif self.MeshType_CB.currentIndex() == 4:                     # UnstructuredMesh
            for radio in [self.Grid_RB, self.MinMax_RB, self.Grid_RB_2, self.MinMax_RB_2, self.Grid_RB_3, self.MinMax_RB_3]:
                radio.hide()
            self.showDialog('Warning', 'Not coded yet !')
        else:
            self.Grid_RB.hide()
            self.MinMax_RB.hide()

    def Create_Mesh(self):
        self.Def_Tallies()

        if self.MeshType_CB.currentIndex() == 0:
            self.showDialog('Warning', 'Select Mesh type first !')
            self.sync_mesh_id()
            return
        elif self.MeshType_CB.currentIndex() in [1, 2, 3, 4, 5]:
            if self.MeshName_LE.text() == '':
                self.showDialog('Warning', 'Cannot create mesh, select name first !')
                return
            elif self.MeshId_LE.text() == '':
                self.showDialog('Warning', 'Cannot create mesh, select id first !')
                return
            else:
                if self.MeshName_LE.text() in self.mesh_name_list:
                    self.showDialog('Warning', 'Mesh name already used, select new name !')
                    return
                elif int(self.MeshId_LE.text()) in self.mesh_id_list:
                    self.showDialog('Warning', 'Mesh id already used, select new id !')
                    return
                else:
                    if self.Mesh_LE_1.text() == '' or self.Mesh_LE_2.text() == '' or self.Mesh_LE_3.text() == '':
                        self.showDialog('Warning', 'Mesh data are missing ! Complete the form !')
                        return
                    else:
                        if self.MeshType_CB.currentIndex() == 1:
                            self.RegularMesh()
                        elif self.MeshType_CB.currentIndex() == 2:
                            self.RectiLinearMesh()
                        elif self.MeshType_CB.currentIndex() == 3:
                            self.CylindricalMesh()
                        elif self.MeshType_CB.currentIndex() == 4:
                            self.SphericalMesh()           
                        elif self.MeshType_CB.currentIndex() == 5:
                            self.UnstructuredMesh()
        if self.No_Error:
            self.mesh_name_list.append(self.MeshName_LE.text())
            self.mesh_id_list.append(self.MeshId_LE.text())
            self.Mesh_ID = int(self.mesh_id_list[-1]) + 1
            self.MeshId_LE.setText(str(self.Mesh_ID))
            if self.AddMeshId_CB.isChecked():
                self.MeshName_LE.setText(self.mesh_suffix + str(self.MeshId_LE.text()))
            else:
                self.MeshName_LE.setText(self.mesh_suffix)

            self.Mesh_LE_1.clear()
            self.Mesh_LE_2.clear()
            self.Mesh_LE_3.clear()
            self.Mesh_1D.setChecked(True)
            self.MeshType_CB.setCurrentIndex(0)
            self.FilterType_CB.setCurrentIndex(0)
            self.Filter_Bins_List_LE.clear()

    def RegularMesh(self):
        self.No_Error = True
        self.LE_to_List(self.Mesh_LE_1)
        dimension = list(map(int, self.List))
        self.LE_to_List(self.Mesh_LE_2)
        LL = list(map(float, self.List))
        self.LE_to_List(self.Mesh_LE_3)
        UR = list(map(float, self.List))
        if LL > UR:
            self.showDialog('Warning', 'Upper_right must be greater than Lower_left !')
            self.No_Error = False
            return
        if self.Mesh_1D.isChecked():
            if len(dimension) != 1:
                self.showDialog('Warning', 'Length of dimension list is not compatible with 1D mesh !')
                self.No_Error = False
                return
            if len(LL) != 1 or len(UR) != 1:
                self.showDialog('Warning', 'Lower_left and Upper_right coordinates number must be equal to 1 !')
                self.No_Error = False
                return
        if self.Mesh_2D.isChecked():
            if len(dimension) != 2:
                self.showDialog('Warning', 'Length of dimension list is not compatible with 2D mesh !')
                self.No_Error = False
                return
            if len(LL) != 2 or len(UR) != 2:
                self.showDialog('Warning', 'Lower_left and Upper_right coordinates number must be equal to 2 !')
                self.No_Error = False
                return
        elif self.Mesh_3D.isChecked():
            if len(dimension) != 3:
                self.showDialog('Warning', 'Length of dimension list is not compatible with 3D mesh !')
                self.No_Error = False
                return
            if len(LL) != 3 or len(UR) != 3:
                self.showDialog('Warning', 'Lower_left or Upper_right coordinates number must be equal to 3 !')
                self.No_Error = False
                return
        print(
            self.MeshName_LE.text() + ' = openmc.' + self.MeshType_CB.currentText() + '(mesh_id=' + self.MeshId_LE.text() + ')\n')
        print(self.MeshName_LE.text() + '.dimension = ' + str(dimension))
        print(self.MeshName_LE.text() + '.lower_left = ' + str(LL))
        print(self.MeshName_LE.text() + '.upper_right = ' + str(UR))

    def RectiLinearMesh(self):
        self.No_Error = True
        self.LE_to_List(self.Mesh_LE_1)
        if self.MinMax_RB.isChecked():
            if len(self.List) != 3:
                self.showDialog('Warning', 'Number of entries must be equal to 3 or check the x_grid radio button !')
                self.No_Error = False
                return
            x_Lower = float(self.List[0])
            x_Upper = float(self.List[1])
            x_Dim   = int(float(self.List[2]))

            if x_Lower > x_Upper :
                self.showDialog('Warning', 'Upper limit must be greater than Lower limit !')
                self.No_Error = False
                return
            msg_x = self.MeshName_LE.text() + '.x_grid = ' + 'np.linspace' + str((x_Lower, x_Upper, x_Dim,))
        else:
            msg_x = self.MeshName_LE.text() + '.x_grid = ' + str(self.List).replace("'", "")
            
        self.LE_to_List(self.Mesh_LE_2)
        if self.MinMax_RB_2.isChecked():
            if len(self.List) != 3:
                self.showDialog('Warning', 'Number of entries must be equal to 3 !')
                self.No_Error = False
                return
            y_Lower = float(self.List[0])
            y_Upper = float(self.List[1])
            y_Dim = int(float(self.List[2]))

            if y_Lower > y_Upper :
                self.showDialog('Warning', 'Upper limit must be greater than Lower limit !')
                self.No_Error = False
                return
            msg_y = self.MeshName_LE.text() + '.y_grid = ' + 'np.linspace' + str((y_Lower, y_Upper, y_Dim,))
        else:
            msg_y = self.MeshName_LE.text() + '.y_grid = ' + str(self.List).replace("'", "")
            
        self.LE_to_List(self.Mesh_LE_3)        
        if self.MinMax_RB_3.isChecked():
            if len(self.List) != 3:
                self.No_Error = False
                self.showDialog('Warning', 'Number of entries must be equal to 3 !')
                return
            z_Lower = float(self.List[0])
            z_Upper = float(self.List[1])
            z_Dim = int(float(self.List[2]))

            if z_Lower > z_Upper:
                self.showDialog('Warning', 'Upper limit must be greater than Lower limit !')
                self.No_Error = False
                return
            msg_z = self.MeshName_LE.text() + '.z_grid = ' + 'np.linspace' + str((z_Lower, z_Upper, z_Dim,))
        else:
            msg_z = self.MeshName_LE.text() + '.z_grid = ' + str(self.List).replace("'", "")

        print(self.MeshName_LE.text() + ' = openmc.' + self.MeshType_CB.currentText() + '(mesh_id=' + self.MeshId_LE.text() + ')\n')
        print(msg_x)
        print(msg_y)
        print(msg_z)

    def CylindricalMesh(self):
        self.No_Error = True
        self.LE_to_List(self.Mesh_LE_1) 
        if self.MinMax_RB.isChecked():
            if len(self.List) != 3:
                self.showDialog('Warning', 'Number of entries must be equal to 3 !')
                self.No_Error = False
                return
            r_Lower = float(self.List[0])
            r_Upper = float(self.List[1])
            r_Dim   = int(float(self.List[2]))
            if r_Lower > r_Upper :
                self.showDialog('Warning', 'Upper limit must be greater than Lower limit !')
                self.No_Error = False
                return
            msg_r = self.MeshName_LE.text() + '.r_grid = ' + 'np.linspace' + str((r_Lower, r_Upper, r_Dim,))
        else:
            msg_r = self.MeshName_LE.text() + '.r_grid = ' + str(self.List).replace("'", "")
        
        self.LE_to_List(self.Mesh_LE_2)
        if self.MinMax_RB_2.isChecked():
            if len(self.List) != 3:
                self.showDialog('Warning', 'Number of entries must be equal to 3 !')
                self.No_Error = False
                return
            if 'pi' in self.List[0] or '*' in self.List[0]:
                phi_Lower = self.List[0].replace('pi', 'np.pi')
            else:
                phi_Lower = float(self.List[0])
            if 'pi' in self.List[1] or '*' in self.List[1]:
                phi_Upper = self.List[1].replace('pi', 'np.pi')
            else:
                phi_Upper = float(self.List[1])
            phi_Dim = int(float(self.List[2]))
            if 'pi' not in self.List[0] and '*' not in self.List[0] and 'pi' not in self.List[1] and '*' not in self.List[1]:
                if phi_Lower > phi_Upper :
                    self.showDialog('Warning', 'Upper limit must be greater than Lower limit !')
                    self.No_Error = False
                    return
            msg_phi = self.MeshName_LE.text() + '.phi_grid = ' + 'np.linspace' + str((phi_Lower, phi_Upper, phi_Dim,)).replace("'", "")
        else:
            msg_phi = self.MeshName_LE.text() + '.phi_grid = ' + str(self.List).replace('pi', 'np.pi').replace("'", "")
        
        self.LE_to_List(self.Mesh_LE_3)
        if self.MinMax_RB_3.isChecked():
            if len(self.List) != 3:
                self.No_Error = False
                self.showDialog('Warning', 'Number of entries must be equal to 3 !')
                return
            z_Lower = float(self.List[0])
            z_Upper = float(self.List[1])
            z_Dim = int(float(self.List[2]))
            if z_Lower > z_Upper :
                self.showDialog('Warning', 'Upper limit must be greater than Lower limit !')
                self.No_Error = False
                return
            msg_z = self.MeshName_LE.text() + '.z_grid = ' + 'np.linspace' + str((z_Lower, z_Upper, z_Dim,))
        else:
            msg_z = self.MeshName_LE.text() + '.z_grid = ' + str(self.List).replace("'", "")

        self.Find_string(self.plainTextEdit, "import numpy")
        if self.Insert_Header:
            self.Find_string(self.v_1, "import numpy")
            if self.Insert_Header:
                print('import numpy as np')

        print(self.MeshName_LE.text() + ' = openmc.' + self.MeshType_CB.currentText() + '(mesh_id=' + self.MeshId_LE.text() + ')\n')
        print(msg_r)
        print(msg_phi)
        print(msg_z)

    def SphericalMesh(self):
        self.No_Error = True
        self.LE_to_List(self.Mesh_LE_1) 
        if self.MinMax_RB.isChecked():
            if len(self.List) != 3:
                self.showDialog('Warning', 'Number of entries must be equal to 3 !')
                self.No_Error = False
                return
            r_Lower = float(self.List[0])
            r_Upper = float(self.List[1])
            r_Dim   = int(float(self.List[2]))
            if r_Lower > r_Upper :
                self.showDialog('Warning', 'Upper limit must be greater than Lower limit !')
                self.No_Error = False
                return
            msg_r = self.MeshName_LE.text() + '.r_grid = ' + 'np.linspace' + str((r_Lower, r_Upper, r_Dim,))
        else:
            msg_r = self.MeshName_LE.text() + '.r_grid = ' + str(self.List).replace("'", "")
        
        self.LE_to_List(self.Mesh_LE_2)
        if self.MinMax_RB_2.isChecked():
            if len(self.List) != 3:
                self.showDialog('Warning', 'Number of entries must be equal to 3 !')
                self.No_Error = False
                return
            if 'pi' in self.List[0] or '*' in self.List[0]:
                theta_Lower = self.List[0].replace('pi', 'np.pi')
            else:
                theta_Lower = float(self.List[0])
            if 'pi' in self.List[1] or '*' in self.List[1]:
                theta_Upper = self.List[1].replace('pi', 'np.pi')
            else:
                theta_Upper = float(self.List[1])
            theta_Dim = int(float(self.List[2]))
            if 'pi' not in self.List[0] and '*' not in self.List[0] and 'pi' not in self.List[1] and '*' not in self.List[1]:
                if theta_Lower > theta_Upper :
                    self.showDialog('Warning', 'Upper limit must be greater than Lower limit !')
                    self.No_Error = False
                    return
            msg_theta = self.MeshName_LE.text() + '.theta_grid = ' + 'np.linspace' + str((theta_Lower, theta_Upper, theta_Dim,)).replace("'", "")
        else:
            msg_theta = self.MeshName_LE.text() + '.theta_grid = ' + str(self.List).replace('pi', 'np.pi').replace("'", "")
        
        self.LE_to_List(self.Mesh_LE_3)
        if self.MinMax_RB_3.isChecked():
            if len(self.List) != 3:
                self.showDialog('Warning', 'Number of entries must be equal to 3 !')
                self.No_Error = False
                return
            if 'pi' in self.List[0] or '*' in self.List[0]:
                phi_Lower = self.List[0].replace('pi', 'np.pi')
            else:
                phi_Lower = float(self.List[0])
            if 'pi' in self.List[1] or '*' in self.List[1]:
                phi_Upper = self.List[1].replace('pi', 'np.pi')
            else:
                phi_Upper = float(self.List[1])
            phi_Dim = int(float(self.List[2]))
            if 'pi' not in self.List[0] and '*' not in self.List[0] and 'pi' not in self.List[1] and '*' not in self.List[1]:
                if phi_Lower > phi_Upper :
                    self.showDialog('Warning', 'Upper limit must be greater than Lower limit !')
                    self.No_Error = False
                    return
            msg_phi = self.MeshName_LE.text() + '.phi_grid = ' + 'np.linspace' + str((phi_Lower, phi_Upper, phi_Dim,)).replace("'", "")
        else:
            msg_phi = self.MeshName_LE.text() + '.phi_grid = ' + str(self.List).replace('pi', 'np.pi').replace("'", "")

        print(self.MeshName_LE.text() + ' = openmc.' + self.MeshType_CB.currentText() + '(mesh_id=' + self.MeshId_LE.text() + ')\n')
        print(msg_r)
        print(msg_theta)
        print(msg_phi)

    def UnstructuredMesh(self):
        self.No_Error = True
        self.showDialog('Warning', 'Under construction !')

    def Create_Filters(self):
        self.Def_Tallies()
        if self.FilterType_CB.currentIndex() == 0:
            self.showDialog('Warning', 'Select Filter type first !')
            self.sync_filter_id()
            return        
        if self.FilterName_LE.text() == '':
            self.showDialog('Warning', 'Cannot create filter, select name first !')
            return
        if self.FilterId_LE.text() == '':
            self.showDialog('Warning', 'Cannot create filter, select id first !')
            return
        if self.FilterName_LE.text() in self.filter_name_list:
            self.showDialog('Warning', 'Filter name already used, select new name !')
            return
        elif int(self.FilterId_LE.text()) in self.filter_id_list:
            self.showDialog('Warning', 'Filter id already used, select new id !')
            return
        if self.FilterType_CB.currentIndex() != 24:
            bins = self.Filter_Bins_List_LE.text().replace("'", "").replace('[', '').replace(']', '')
            self.Filter_Bins_List_LE.setText(bins)


        if self.FilterType_CB.currentIndex() in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 25]:
            if self.Filter_Bins_List_LE.text() == '':
                self.showDialog('Warning', 'No filter bins selected')
                return
            else:
                self.LE_to_List(self.Filter_Bins_List_LE)
                bins = self.List
                if self.FilterType_CB.currentIndex() in [1, 2, 3, 4, 5, 6, 8, 9, 10, 16]:
                    difference = list(set(bins) - set(self.Allowed_Filter_Bins))
                    if difference:
                        self.showDialog('Warning', 'The following bins ' + str(difference).replace("'", '') + ' are not in actual bins !')
                        remaining = list(set(bins) - set(difference))
                        if remaining:
                            self.Filter_Bins_List_LE.setText(str(sorted(remaining)))
                        else:
                            self.Filter_Bins_List_LE.clear()
                        return
                elif self.FilterType_CB.currentIndex() in [7, 25]:
                    bins = list(set(map(int, bins)))
            bins.sort()
            if self.FilterType_CB.currentIndex() not in [6, 9, 16]:
                print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(' + str(
                      bins).replace("'", "") + ', filter_id=' + self.FilterId_LE.text() + ')')
            elif self.FilterType_CB.currentIndex() == 6:
                instances = ''
                for cell in self.Filter_Bins_List:
                    instance = '[(' + cell + ', i) for i in range(' + cell + '.num_instances)]'
                    if len(self.Filter_Bins_List) == 1:
                        instances += '(' + instance + ')'
                    elif cell == self.Filter_Bins_List[0]:
                        instances += '(' + instance + ' +\n'
                    elif cell == self.Filter_Bins_List[-1]:
                        instances += '             ' + instance + ')'
                    else:
                        instances += '             ' + instance + ' +\n'
                print('instances = ' + instances)
                print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(instances ' + ', filter_id=' + self.FilterId_LE.text() + ')')
            elif self.FilterType_CB.currentIndex() in [9, 16]:
                if len(self.Filter_Bins_List) != 1:
                    self.showDialog('Warning', 'Only first bin will be considered !')
                print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(' +
                      self.Filter_Bins_List[0] + ', filter_id=' + self.FilterId_LE.text() + ')')

        elif self.FilterType_CB.currentIndex() in [11, 12, 13, 14, 15]:
            if self.Filter_Bins_CB.currentIndex() == 0:
                self.showDialog('Warning', 'Select option first !')
                return
            elif self.Filter_Bins_CB.currentIndex() in [1, 2]:
                if self.Filter_Bins_List_LE.text() == '':
                    self.showDialog('Warning', 'No filter bins selected !')
                    return
                else:
                    self.LE_to_List(self.Filter_Bins_List_LE)
                    bins = self.List
                    if 'pi' in bins or '*' in bins:
                        bins = [item.replace('pi', 'np.pi') for item in bins] 
                    else:
                        bins = list(set(map(float, bins)))
                        bins.sort()

                    print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(' + str(
                          bins).replace("'", "") + ', filter_id=' + self.FilterId_LE.text() + ')')

            elif self.Filter_Bins_CB.currentIndex() in [3, 4]:
                if self.Start_LE.text() == '':
                    self.showDialog('Warning', 'Enter Start Value first !')
                    return
                elif self.End_LE.text() == '':
                    self.showDialog('Warning', 'Enter End Value first !')
                    return
                elif self.GrpNumber_LE.text() == '':
                    self.showDialog('Warning', 'Enter Groups number first !')
                    return
                else:
                    if self.Filter_Bins_CB.currentIndex() == 3:
                        self.Create_Equal_Step_Grid()

            if self.FilterType_CB.currentIndex() in [11, 12]:
                if self.Filter_Bins_CB.currentIndex() == 4:
                    self.Create_Equal_Lethargy_Energy_Grid()
                elif self.Filter_Bins_CB.currentIndex() == 5:
                    if self.MGX_CB.currentIndex() == 0:
                        self.showDialog('Warning', 'Select MGX Structure first !')
                        return
                    else:
                        self.MGX_GROUP_STRUCTURES()
        elif self.FilterType_CB.currentIndex() == 17:
            if self.GrpNumber_LE.text() == '':
                self.showDialog('Warning', 'No filter bins selected !')
                return
            else:
                self.LE_to_List(self.GrpNumber_LE)
                bins = self.List
                bins = list(set(map(int, bins)))
                bins.sort()
                for item in bins:
                    if item not in [1, 2, 3, 4, 5, 6]:
                        self.showDialog('Warning', 'Input groups may not be compatible with ENDF/B-VII.1 which uses 6 precursor groups !')
                print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(' + str(
                    bins).replace("'", "") + ', filter_id=' + self.FilterId_LE.text() + ')')
        elif self.FilterType_CB.currentIndex() == 18:
            if self.Start_LE.text() == '':
                self.showDialog('Warning', 'No grid of energy values entered!')
                return
            elif self.End_LE.text() == '':
                self.showDialog('Warning', 'No grid of interpolant values  entered!')
                return
            else:
                self.LE_to_List(self.Start_LE)
                bins_1 = self.List
                bins_1 = list(set(map(float, bins_1)))
                self.LE_to_List(self.End_LE)
                bins_2 = self.List
                bins_2 = list(set(map(float, bins_2)))
                print('energy = ' + str(bins_1).replace("'", ""))
                print('y = ' + str(bins_2).replace("'", ""))
                print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(energy, y'
                      + ', filter_id=' + self.FilterId_LE.text() + ')')
        elif self.FilterType_CB.currentIndex() in [19, 21]:
            print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(order= ' + self.GrpNumber_LE.text()
                  + ', filter_id=' + self.FilterId_LE.text() + ')')
        elif self.FilterType_CB.currentIndex() == 20:
            if self.MGX_CB.currentIndex() == 0:
                self.showDialog('Warning', 'Select axis first !')
                return
            print(self.MGX_CB.currentText() + 'min = ', self.Start_LE.text())
            print(self.MGX_CB.currentText() + 'max = ', self.End_LE.text())
            print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(order= ' + self.GrpNumber_LE.text()
                  + ", '" + self.MGX_CB.currentText() + "', axis=" + self.MGX_CB.currentText() + 'minimum= min' + ', ' 
                  + self.MGX_CB.currentText() + 'maximum= max' + ', filter_id=' + self.FilterId_LE.text() + ')')
        elif self.FilterType_CB.currentIndex() in [22, 23]:
            if self.Start_LE.text() == '' or self.End_LE.text() == '' or self.GrpNumber_LE.text() == '' or self.Filter_Bins_List_LE.text() == '':
                self.showDialog('Warning', 'Enter data first !')
                return
            else:
                print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(order= ' + self.Filter_Bins_List_LE.text()
                    + ", x= " + self.Start_LE.text() + ", y= " + self.End_LE.text() + ', r= ' + self.GrpNumber_LE.text() +
                      ', filter_id=' + self.FilterId_LE.text() + ')')
        elif self.FilterType_CB.currentIndex() == 24:
            print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(' +
                str(self.Filter_Bins_List_LE.text()) + ', filter_id=' + self.FilterId_LE.text() + ')')
        index = self.Filters_List_CB.findText('Select Filter')
        if index == -1:
            self.Filters_List_CB.addItems(['Select Filter', 'All filters'])
            self.Filters_List_CB.addItems(self.filter_name_list)
        self.Filters_List_CB.addItem(self.FilterName_LE.text())
        self.filter_name_list.append(self.FilterName_LE.text())
        self.filter_id_list.append(self.FilterId_LE.text())
        self.Filter_ID = int(self.filter_id_list[-1]) + 1
        self.FilterId_LE.setText(str(self.Filter_ID))
        self.FilterType_CB.setCurrentIndex(0)
        self.FilterName_LE.setText('_filter')
        self.Filter_Bins_List_LE.clear()
        self.GrpNumber_LE.clear()
        self.Start_LE.clear()
        self.End_LE.clear()
        self.sync_filter_id()
        self.Show_Hide_Widgets()

    def Update_Filters(self):
        self.Filter_Bins_List = []
        self.Allowed_Filter_Bins = []
        if self.FilterType_CB.currentIndex() in [1, 2, 3, 4, 5, 6, 8, 9, 10, 16]:
            self.Filter_Bins_CB.setEnabled(True)
            self.Filter_Bins_List_LE.setValidator(None)
        elif self.FilterType_CB.currentIndex() in [11, 12]:
            self.Filter_Bins_CB.setEnabled(True)
            self.Filter_Bins_CB.clear()
            self.Filter_Bins_CB.addItems(['Select option', 'Enter data', 'Load text file', 'Equal-Step Energies', 'Equal-Lethargy Energies', 'MGX.GRP_STRUCTURES'])
            self.Filter_Bins_List_LE.setValidator(self.float_validator_list_positif)
            if self.Filter_Bins_CB.currentIndex() == 1:
                self.Filter_Bins_List_LE.setValidator(self.float_validator_list_positif)
            else:
                self.Filter_Bins_List_LE.setValidator(None)
        elif self.FilterType_CB.currentIndex() in [13, 14, 15]:
            self.Filter_Bins_CB.setEnabled(True)
            self.Filter_Bins_CB.clear()
            if self.FilterType_CB.currentIndex() == 13:
                self.Filter_Bins_CB.addItems(['Select option', 'Enter data', 'Load text file', 'Equal-Step Mu'])
            elif self.FilterType_CB.currentIndex() == 14:
                self.Filter_Bins_CB.addItems(['Select option', 'Enter data', 'Load text file', 'Equal-Step polar angle'])
            if self.FilterType_CB.currentIndex() == 15:
                self.Filter_Bins_CB.addItems(['Select option', 'Enter data', 'Load text file', 'Equal-Step azimutal angle'])
        else:
            self.Filter_Bins_CB.setEnabled(False)
        if self.FilterType_CB.currentIndex() == 0:
            self.FilterName_LE.setText('_filter')
            self.Filter_Bins_CB.clear()
        elif self.FilterType_CB.currentIndex() not in [11, 12, 13, 14, 15]:
            self.FilterName_LE.setText(self.FILTER_SUFFIX[self.FilterType_CB.currentIndex() - 1].replace("'", ''))
            self.Filter_Bins_CB.clear()
            self.Filter_Bins_CB.addItem('Select bins')
            if self.FilterType_CB.currentIndex() in [1, 2, 3, 4, 5, 8, 10]:  # !!!!!!!!!!!!!!!!!!!!!!
                self.Filter_Bins_CB.addItem('All bins')
            if self.FilterType_CB.currentIndex() in [1, 2, 3, 4, 5, 6, 8, 9, 10, 16]:
                self.Allowed_Filter_Bins = self.Availble_Filters[self.FilterType_CB.currentText()]
                self.Filter_Bins_CB.addItems(self.Allowed_Filter_Bins)
        if self.FilterType_CB.currentIndex() == 0:
            self.FilterName_LE.setText('_filter')
        elif self.FilterType_CB.currentIndex() == 24:
            self.Filter_Bins_CB.addItem('All bins')
            self.Filter_Bins_CB.addItems(self.PARTICLE_TYPE)
            self.Filter_Bins_CB.setEnabled(True)
        else:
            self.FilterName_LE.setText(self.FILTER_SUFFIX[self.FilterType_CB.currentIndex() - 1].replace("'", ''))

        self.sync_filter_id()

    def Import_Grid_List(self, LineEd):
        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "~", "*;; *.inp;; *.dat;; *.txt")[0]
        x = []
        if file:
            f = open(file, "r")
            lines = f.readlines()
            for line in lines:
                for separator in [',', ';', ':', ' ']:
                    if separator in line:
                        line.replace(separator, ' ')
                x.append(line.split())
            f.close()
            LineEd.setText(str(x).replace("'", ""))

    def Create_Equal_Step_Grid(self):
        self.Find_string(self.plainTextEdit, "import numpy")
        if self.Insert_Header:
            self.Find_string(self.v_1, "import numpy")
            if self.Insert_Header:
                print('import numpy as np')
        variable = self.FilterType_CB.currentText().replace('Filter', '')
        Start = self.Start_LE.text().replace('pi', 'np.pi')
        End = self.End_LE.text().replace('pi', 'np.pi')
        print(variable + ' = np.linspace(' + Start + ', ' + End + ', ' + self.GrpNumber_LE.text() + ', endpoint=True)')
        print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(' + variable + ', filter_id=' + self.FilterId_LE.text() + ')')

    def Create_Equal_Lethargy_Energy_Grid(self):
        self.Find_string(self.plainTextEdit, "import numpy")
        if self.Insert_Header:
            self.Find_string(self.v_1, "import numpy")
            if self.Insert_Header:
                print('import numpy as np')
        variable = self.FilterType_CB.currentText().replace('Filter', '')
        print(variable + ' = np.logspace(np.log10(' + self.Start_LE.text() + '), np.log10(' + self.End_LE.text() + '), ' + self.GrpNumber_LE.text() + ')')
        print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + '(' + variable + ', filter_id=' + self.FilterId_LE.text() + ')')

    def MGX_GROUP_STRUCTURES(self):
        print(self.FilterName_LE.text() + ' = openmc.' + self.FilterType_CB.currentText() + "(openmc.mgxs.GROUP_STRUCTURES['" + self.MGX_CB.currentText() + "'], filter_id=" + self.FilterId_LE.text() + ')')

    def Update_Filter_Bins(self):
        if self.FilterType_CB.currentIndex() in [1, 2, 3, 4, 5, 6, 8, 9, 10, 16]:
            self.Filter_Bins_List_LE.setValidator(None)
        elif self.FilterType_CB.currentIndex() in [11, 12]:   # EnergyFilter
            if self.Filter_Bins_CB.currentIndex() == 1:
                self.Filter_Bins_List_LE.setValidator(self.float_validator_list_positif)
            elif self.Filter_Bins_CB.currentIndex() in [3, 4]:
                self.Start_LE.setValidator(self.validator_positif)
                self.End_LE.setValidator(self.validator_positif)
            else:
                self.Filter_Bins_List_LE.setValidator(None)
        elif self.FilterType_CB.currentIndex() == 13:      #  MuFilter
            if self.Filter_Bins_CB.currentIndex() == 1:
                self.Filter_Bins_List_LE.setValidator(self.float_validator_list)
            elif self.Filter_Bins_CB.currentIndex() == 3:
                self.Start_LE.setValidator(self.validator)
                self.End_LE.setValidator(self.validator)
            else:
                self.Filter_Bins_List_LE.setValidator(None)
        elif self.FilterType_CB.currentIndex() == 14:     # polarFilter
            if self.Filter_Bins_CB.currentIndex() == 1:
                self.Filter_Bins_List_LE.setValidator(self.float_validator_list_pi_positif)
            elif self.Filter_Bins_CB.currentIndex() == 3:
                self.Start_LE.setValidator(self.float_validator_pi_positif)
                self.End_LE.setValidator(self.float_validator_pi_positif)
            else:
                self.Filter_Bins_List_LE.setValidator(None)
        elif self.FilterType_CB.currentIndex() == 15:      # azimutalFilter
            if self.Filter_Bins_CB.currentIndex() == 1:
                self.Filter_Bins_List_LE.setValidator(self.float_validator_list_pi)
            elif self.Filter_Bins_CB.currentIndex() == 3:
                self.Start_LE.setValidator(self.float_validator_pi)
                self.End_LE.setValidator(self.float_validator_pi)
            else:
                self.Filter_Bins_List_LE.setValidator(None)


        if self.FilterType_CB.currentIndex() not in [6, 9, 11, 12, 13, 14, 15, 16]:
            if self.Filter_Bins_CB.currentIndex() not in [0, 1] and self.Filter_Bins_CB.currentText() not in self.Filter_Bins_List:
                self.Filter_Bins_List.append(self.Filter_Bins_CB.currentText())
            if self.Filter_Bins_CB.currentIndex() == 0:
                pass
            elif self.Filter_Bins_CB.currentIndex() == 1:
                self.Use_AllItems = True
                AllItems = [self.Filter_Bins_CB.itemText(i) for i in range(self.Filter_Bins_CB.count())][2:]
                self.Filter_Bins_List = AllItems
                self.Filter_Bins_List_LE.setText(str(self.Filter_Bins_List))
            else:
                if self.Use_AllItems:
                    self.Filter_Bins_List_LE.clear()
                    self.Use_AllItems = False
                self.Filter_Bins_List_LE.setText(str(self.Filter_Bins_List))
        elif self.FilterType_CB.currentIndex() in [11, 12, 13, 14, 15]:
            if self.Filter_Bins_CB.currentIndex() == 2:
                self.Import_Grid_List(self.Filter_Bins_List_LE)
            elif self.Filter_Bins_CB.currentIndex() == 5:
                self.MGX_CB.clear()
                self.MGX_CB.addItems(self.MGX_GROUP_STRUCTURES_LIST)
        else:
            if self.Filter_Bins_CB.currentIndex() != 0 and self.Filter_Bins_CB.currentText() not in self.Filter_Bins_List:
                self.Filter_Bins_List.append(self.Filter_Bins_CB.currentText())
                self.Filter_Bins_List_LE.setText(str(self.Filter_Bins_List))

    def Choose_MGX_STR(self):
        if self.MGX_CB.currentIndex() != 0:
            self.Filter_Bins_List_LE.clear()
            self.Filter_Bins_List_LE.setText(self.MGX_CB.currentText())

    def Show_Hide_Widgets(self):
        self.Filter_Bins_List_LE.show()
        self.Filter_Bins_List_LE.clear()
        self.Undo_PB.show()
        self.Reset_PB.show()
        if self.FilterType_CB.currentIndex() in [11, 12, 13, 14, 15]:
            self.Filter_Bins_CB.show()
            self.label_8.setText('Start Value')
            self.label_10.setText('End Value')
            self.label.setText('Groups number')
            if self.Filter_Bins_CB.currentIndex() in [3, 4]:
                for item in [self.label, self.label_8, self.label_10, self.Start_LE, self.End_LE,
                             self.GrpNumber_LE]:
                    item.show()
                self.MGX_CB.hide()
                self.Start_LE.setValidator(self.validator)
                self.End_LE.setValidator(self.validator)
            else:
                if self.Filter_Bins_CB.currentIndex() == 5:
                    self.MGX_CB.show()
                else:
                    self.MGX_CB.hide()
                for item in [self.label, self.label_8, self.label_10, self.Start_LE, self.End_LE, self.GrpNumber_LE]:
                    item.hide()
        elif self.FilterType_CB.currentIndex() == 17:
            for item in [self.label_8, self.label_10, self.Start_LE, self.End_LE]:
                item.hide()
            self.label.show()
            self.Filter_Bins_CB.hide()
            self.GrpNumber_LE.setValidator(self.dim_validator)
            self.GrpNumber_LE.show()
            self.label.setText('Delayed Group number')
            self.Undo_PB.hide()
            self.Reset_PB.hide()
        elif self.FilterType_CB.currentIndex() == 18:
            for item in [self.label_8, self.label_10, self.Start_LE, self.End_LE]:
                item.show()
            self.label.hide()
            self.GrpNumber_LE.hide()
            self.Filter_Bins_CB.hide()
            self.Undo_PB.hide()
            self.Reset_PB.hide()
            self.label_8.setText('Energy values in [eV]')
            self.label_10.setText('Interpolant values in [eV]')
            for LineEd in [self.Start_LE, self.End_LE]:
                LineEd.setValidator(self.float_validator_list)
        elif self.FilterType_CB.currentIndex() in [19, 21]:
            self.Filter_Bins_CB.hide()
            for item in [self.label, self.GrpNumber_LE]:
                item.show()
            for item in [self.MGX_CB, self.label_8, self.label_10, self.Start_LE, self.End_LE]:
                item.hide()
            self.Undo_PB.hide()
            self.Reset_PB.hide()
            if self.FilterType_CB.currentIndex() == 19:
                self.label.setText('Legend order')
            elif self.FilterType_CB.currentIndex() == 21:
                self.label.setText('Spherical Harmonics order')
            self.GrpNumber_LE.setValidator(self.int_validator)
        elif self.FilterType_CB.currentIndex() == 20:
            for item in [self.label_8, self.label, self.label_10, self.Start_LE, self.End_LE, self.GrpNumber_LE]:
                item.show()
            self.Filter_Bins_CB.hide()
            self.MGX_CB.show()
            self.MGX_CB.clear()
            self.MGX_CB.addItems(['Select axis', 'x', 'y', 'z'])
            self.GrpNumber_LE.setValidator(self.int_validator)
            self.Start_LE.setValidator(self.validator)
            self.End_LE.setValidator(self.validator)
        elif self.FilterType_CB.currentIndex() in [22, 23]:
            for item in [self.Filter_Bins_List_LE, self.label_8, self.label, self.label_10, self.Start_LE, self.End_LE, self.GrpNumber_LE]:
                item.show()
            self.label_8.setText('x')
            self.label_10.setText('y')
            self.label.setText('radius')
            self.Filter_Bins_List_LE.setValidator(self.int_validator)
            self.GrpNumber_LE.setValidator(QDoubleValidator(self))
        else:
            for item in [self.MGX_CB, self.label, self.label_8, self.label_10, self.Start_LE, self.End_LE,
                         self.GrpNumber_LE]:
                item.hide()
            self.Filter_Bins_CB.show()
        if self.FilterType_CB.currentIndex() in [22, 23]:
            self.label_7.setText('Zernike polynomials order')
        else:
            self.label_7.setText('Filter Bins')
            self.Filter_Bins_List_LE.setValidator(None)

    def Show_Hide_Widgets_1(self):

            if self.MGX_CB.currentIndex() == 0:
                self.label_8.setText('min')
                self.label_10.setText('max')
                self.label.setText('Legend order')
            else:
                self.label_8.setText(self.MGX_CB.currentText() + 'min')
                self.label_10.setText(self.MGX_CB.currentText() + 'max')
                self.label.setText('Legend order')
            self.Undo_PB.hide()
            self.Reset_PB.hide()

    def Add_Nuclides_Bins_To_Tally(self):
        if self.Nuclides_CB.currentIndex() not in [0, 1] and self.Nuclides_CB.currentText() not in self.Nuclides_Bins_List:
            self.Nuclides_Bins_List.append(self.Nuclides_CB.currentText())
        if self.Nuclides_CB.currentIndex() == 0:
            pass
        elif self.Nuclides_CB.currentIndex() == 1:
            self.Use_AllItems = True
            AllItems = [self.Nuclides_CB.itemText(i) for i in range(self.Nuclides_CB.count())][2:]
            self.Nuclides_Bins_List = AllItems
            self.Nuclides_Bins_List_LE.setText(str(self.Nuclides_Bins_List))
        else:
            if self.Use_AllItems:
                self.Nuclides_Bins_List_LE.clear()
                self.Use_AllItems = False
            self.Nuclides_Bins_List_LE.setText(str(self.Nuclides_Bins_List))
        self.Nuclides_CB.setCurrentIndex(0)

    def Def_Filters_Bins_To_Tally(self):
        if self.Filters_List_CB.currentIndex() not in [0, 1] and self.Filters_List_CB.currentText() not in self.Filters_List:
            self.Filters_List.append(self.Filters_List_CB.currentText())
        if self.Filters_List_CB.currentIndex() == 0:
            pass
        elif self.Filters_List_CB.currentIndex() == 1:
            self.Use_AllItems = True
            AllItems = [self.Filters_List_CB.itemText(i) for i in range(self.Filters_List_CB.count())][2:]
            self.Filters_List = AllItems
            self.Filters_List_LE.setText(str(self.Filters_List))
        else:
            if self.Use_AllItems:
                self.Filters_List_LE.clear()
                self.Use_AllItems = False
            self.Filters_List_LE.setText(str(self.Filters_List))
        self.Filters_List_CB.setCurrentIndex(0)

    def Add_Filters_Bins_To_Tally(self):
        if self.Filters_List_LE.text():
            if not self.Create_New_Tally and self.tally_name_list:
                qm = QMessageBox
                ret = qm.question(self, 'Warning', 'No new tally created. Tally ' + self.tally_name_list[-1] +  ' will be modified! proceed?', qm.Yes | qm.No)
                if ret == qm.No:
                    return

            if self.tally_name_list:
                document = self.plainTextEdit.toPlainText()
                lines = document.split('\n')
                for line in lines:
                    if (self.tally_name_list[-1] + ".filters" in line):
                        lines.remove(line)
                        document = self.plainTextEdit.toPlainText().replace(line,"")
                self.plainTextEdit.clear()
                self.plainTextEdit.insertPlainText(document)
                print(self.tally_name_list[-1] + '.filters = ' + self.Filters_List_LE.text().replace("'", ""))
            else:
                self.showDialog('Warning', 'Add tally first !')
        else:
            self.showDialog('Warning', 'Choose filters to add first !')
            return
        self.Filters_List_CB.setCurrentIndex(0)
        self.Filters_List_LE.clear()
        self.Reset(self.Filters_List, self.Filters_List_LE)

    def LE_to_List(self, LineEdit):
        self.List = []
        text = LineEdit.text().replace('(', '').replace(')', '')
        for separator in [',', ';', ':', ' ']:
            if separator in text:
                text = str(' '.join(text.replace(separator, ' ').split()))
        self.List = text.split()
        return self.List

    def Add_Nuclides(self):
        if self.Nuclides_Bins_List_LE.text() == '':
            self.showDialog('Warning', 'No Nuclide selected !')
            return
        if not self.Create_New_Tally and self.tally_name_list:
            qm = QMessageBox
            ret = qm.question(self, 'Warning', 'No new tally created. Tally ' + self.tally_name_list[-1] +  ' will be modified! proceed?', qm.Yes | qm.No)
            if ret == qm.No:
                return

        Nuclides = self.Nuclides_Bins_List_LE.text()
        nuclides_list = Nuclides[Nuclides.find("[") + 1: Nuclides.find("]")].replace("'","").replace(" ","").split(',')
        
        if self.tally_name_list:
            document = self.plainTextEdit.toPlainText()
            lines = document.split('\n')
            for line in lines:
                if (".nuclides" in line):
                    lines.remove(line)
                    document = self.plainTextEdit.toPlainText().replace(line,"")
            self.plainTextEdit.clear()
            self.plainTextEdit.insertPlainText(document)
            for item in nuclides_list:
                if item not in self.Model_Nuclides_List:
                    self.showDialog('Warning', item + ' not in list of nuclides in the model!')
                    return
            print(self.tally_name_list[-1] + '.nuclides = ' + Nuclides)
            self.Nuclides_Bins_List_LE.clear()
        else:
            self.showDialog('Warning', 'Add tally first !')
            return
        self.Reset(self.Nuclides_Bins_List, self.Nuclides_Bins_List_LE)

    def Add_Scores(self):
        if self.ScoresList_LE.text() == '':
            self.showDialog('Warning', 'No score to add !')
            return
        if not self.Create_New_Tally and self.tally_name_list:
            qm = QMessageBox
            ret = qm.question(self, 'Warning', 'No new tally created. Tally ' + self.tally_name_list[-1] +  ' will be modified! proceed?', qm.Yes | qm.No)
            if ret == qm.No:
                return

        scores = self.ScoresList_LE.text()
        if self.tally_name_list:
            document = self.plainTextEdit.toPlainText()
            lines = document.split('\n')
            for line in lines:
                if (".scores" in line):
                    lines.remove(line)
                    document = self.plainTextEdit.toPlainText().replace(line,"")
            self.plainTextEdit.clear()
            self.plainTextEdit.insertPlainText(document)
            print(self.tally_name_list[-1] + '.scores = ' + scores )
            if self.Estimator_CB.currentIndex()!= 0:
                print(self.tally_name_list[-1] + '.estimator = ' + "'" + str(self.Estimator_CB.currentText() + "'"))
            self.ScoresList_LE.clear()
            self.FluxScores_CB.setCurrentIndex(0)
            self.RxnRates_CB.setCurrentIndex(0)
            self.PartProduction_CB.setCurrentIndex(0)
            self.MiscScores_CB.setCurrentIndex(0)
        else:
            self.showDialog('Warning', 'Add tally first !')
            return
        self.Reset(self.Scores_List, self.ScoresList_LE)

    def DEF_FluxScores(self):
        self.Use_AllItems = False
        if self.FluxScores_CB.currentText() not in self.Scores_List:
            if self.FluxScores_CB.currentIndex() != 0:
                self.Scores_List.append(self.FluxScores_CB.currentText())
            self.Update_Scores_LE()

    def DEF_RxnRates(self):
        self.Use_AllItems = False
        if self.RxnRates_CB.currentText() not in self.Scores_List:
            if self.RxnRates_CB.currentIndex() != 0:
                self.Scores_List.append(self.RxnRates_CB.currentText())
            self.Update_Scores_LE()

    def DEF_PartProduction(self):
        self.Use_AllItems = False
        if self.PartProduction_CB.currentText() not in self.Scores_List:
            if self.PartProduction_CB.currentIndex() != 0:
                self.Scores_List.append(self.PartProduction_CB.currentText())
            self.Update_Scores_LE()

    def DEF_MiscScores(self):
        self.Use_AllItems = False
        if self.MiscScores_CB.currentText() not in self.Scores_List:
            if self.MiscScores_CB.currentIndex() != 0:
                self.Scores_List.append(self.MiscScores_CB.currentText())
            self.Update_Scores_LE()

    def Update_Scores_LE(self):
        self.ScoresList_LE.clear()
        self.ScoresList_LE.setText(str(self.Scores_List))
        self.FluxScores_CB.setCurrentIndex(0)
        self.RxnRates_CB.setCurrentIndex(0)
        self.PartProduction_CB.setCurrentIndex(0)
        self.MiscScores_CB.setCurrentIndex(0)

    def Find_Tallies(self):
        self.Find_Filters()
        self.Find_Scores()
        self.Store_Tallies_Info(self.Tally, self.Tally_ID)

    def Store_Tallies_Info(self, Tally, Tally_Id):
        # new dictionary filling : parent
        self.Tallies_In_Model[Tally] = {}
        self.Tallies_In_Model[Tally]['id'] = Tally_Id
        self.Tallies_In_Model[Tally]['name'] = Tally
        self.Tallies_In_Model[Tally]['title'] = self.TallyName

    def Def_Tallies(self):
        self.Find_string(self.plainTextEdit, "import openmc")
        if self.Insert_Header:
            self.Find_string(self.v_1, "import openmc")
            if self.Insert_Header:
                print('import openmc')

        self.Find_string(self.v_1, "openmc.Tallies")
        if self.Insert_Header:
            self.Find_string(self.plainTextEdit, "openmc.Tallies")
            if self.Insert_Header:
                print('\n###############################################################################\n'
                        '#                 Exporting to OpenMC tallies.xml file \n'
                        '###############################################################################')
                print("tallies = openmc.Tallies()\n")
            else:
                pass

    def Export_Tallies(self):
        if self.Tallies_Tab.currentIndex() == 1 and self.tally_name_list[-1] + '.scores' not in self.plainTextEdit.toPlainText():
            self.showDialog('Warning', 'will not create XML for Tally ID=' + self.tally_id_list[-1] + ' since it does not contain any score')
        else:
            if 'import numpy' in self.plainTextEdit.toPlainText():
                self.Suppress_Line('import numpy', self.plainTextEdit)
            self.v_1.moveCursor(QTextCursor.End)
            if self.Tallies_Tab.currentIndex() == 1:
                print('\ntallies.append(' + self.tally + ')')
            string_to_find = "tallies.export_to_xml()"
            self.Find_string(self.v_1, string_to_find)

            cursor = self.v_1.textCursor()
            self.plainTextEdit.moveCursor(QTextCursor.End)
            if self.Insert_Header:
                if self.Tallies_Tab.currentIndex() == 1:
                    print('\n' + string_to_find)
                cursor.insertText(self.plainTextEdit.toPlainText())
            else:
                #if self.Tallies_Tab.currentIndex() == 1:
                print('\n' + string_to_find)
                
                document = self.v_1.toPlainText().replace(string_to_find, self.plainTextEdit.toPlainText())
                self.v_1.clear()
                cursor = self.v_1.textCursor()
                cursor.insertText(document)

                '''if 'DistribcellFilter' in self.v_1.toPlainText():
                    self.showDialog('', 'Distribcell')
                    self.Find_string(self.v_1, "import openmc.lib")
                    if self.Insert_Header:
                        cursor.setPosition(0)
                        cursor.insertText('import openmc.lib\n')'''

            self.text_inserted = True
            self.plainTextEdit.clear()
            self.Create_New_Tally = False

    def Suppress_Line(self, item, TextEdit):
        text = TextEdit.toPlainText()
        TextEdit.clear()
        for l in text.split('\n'):
            if item in l:
                Line = l
                text = text.replace(l, '')
                _list = text.split('\n')
                _list = [ i for i in _list if i ]
                text = '\n'.join(_list)
                cursor = TextEdit.textCursor()
                cursor.insertText(text)
                cursor = self.v_1.textCursor()
                cursor.setPosition(0)
                cursor.insertText(Line + '\n')
                

    def Find_string(self, text_window, string_to_find):
        self.list_of_items = []
        self.current_line = ''
        self.line_number = 0
        self.Insert_Header = True
        document = text_window.toPlainText()
        for line in document.split('\n'):
            self.line_number += 1
            if string_to_find in line:
                self.current_line = line
                self.list_of_items.append(line[0:len(line) -1])
                self.Insert_Header = False

    def Undo(self, List, LineEdit):
        if List:
            if self.Use_AllItems:
                List.clear()
                LineEdit.clear()
            else:
                List.pop()
            LineEdit.setText(str(List))
            if not List:
                LineEdit.clear()
            return List
        self.Use_AllItems = False

    def Reset(self, List, LineEdit):
        List.clear()
        LineEdit.clear()
        return List
        self.Use_AllItems = False

    def clear_text(self, text):
        if text != "\n":
            if self.text_inserted:
                self.plainTextEdit.clear()
            else:
                qm = QMessageBox
                ret = qm.question(self, 'Warning', 'Do you really want to clear data ?', qm.Yes | qm.No)
                if ret == qm.Yes:
                    self.plainTextEdit.clear()
                elif ret == qm.No:
                    pass

    def normalOutputWritten(self,text):
        self.highlighter = Highlighter(self.plainTextEdit.document())
        cursor = self.plainTextEdit.textCursor()
        cursor.insertText(text)
