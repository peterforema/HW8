# region imorts
import numpy as np
import matplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import PyQt5.QtWidgets as qtw

# importing from previous work on least squares fit
from LeastSquares import LeastSquaresFit_Class


# endregion

# region class definitions
class Pump_Model():
    """
    This is the pump model.  It just stores data.
    """

    def __init__(self):  # pump class constructor
        # create some class variables for storing information
        self.PumpName = ""
        self.FlowUnits = ""
        self.HeadUnits = ""

        # place to store data from file
        self.FlowData = np.array([])
        self.HeadData = np.array([])
        self.EffData = np.array([])

        # place to store coefficients for cubic fits
        self.HeadCoefficients = np.array([])
        self.EfficiencyCoefficients = np.array([])

        # create two instances (objects) of least squares class
        self.LSFitHead = LeastSquaresFit_Class()
        self.LSFitEff = LeastSquaresFit_Class()


class Pump_Controller():
    def __init__(self):
        self.Model = Pump_Model()
        self.View = Pump_View()

    # region functions to modify data of the model
    def ImportFromFile(self, data):
        """
        This processes the list of strings in data to build the pump model
        :param data:
        :return:
        """
        # Inside Pump_Controller.ImportFromFile
        self.Model.PumpName = data[0].strip()
        units = data[1].split()
        self.Model.FlowUnits = units[0]
        self.Model.HeadUnits = units[1]
        self.SetData(data[3:])

        # extracts flow, head and efficiency data and calculates coefficients
        self.SetData(data[3:])
        self.updateView()

    def SetData(self, data):
        '''
        Expects three columns of data in an array of strings with space delimiter
        Parse line and build arrays.
        :param data:
        :return:
        '''
        # erase existing data
        self.Model.FlowData = np.array([])
        self.Model.HeadData = np.array([])
        self.Model.EffData = np.array([])

        # parse new data
        for L in data:
            Cells =  L.split()#parse the line into an array of strings
            self.Model.FlowData = np.append(self.Model.FlowData, float(Cells[0]))
            self.Model.HeadData = np.append(self.Model.HeadData, float(Cells[1]))
            self.Model.EffData = np.append(self.Model.EffData, float(Cells[2]))

            # call least square fit for head and efficiency
            self.LSFit()

    def LSFit(self):
        '''Fit cubic polynomial using Least Squares'''
        self.Model.LSFitHead.x = self.Model.FlowData
        self.Model.LSFitHead.y = self.Model.HeadData
        self.Model.LSFitHead.LeastSquares(3)  # calls LeastSquares function of LSFitHead object

        self.Model.LSFitEff.x = self.Model.FlowData
        self.Model.LSFitEff.y = self.Model.EffData
        self.Model.LSFitEff.LeastSquares(3)  # calls LeastSquares function of LSFitEff object

    # endregion

    # region functions interacting with view
    def setViewWidgets(self, w):
        self.View.setViewWidgets(w)

    def updateView(self):
        self.View.updateView(self.Model)
    # endregion


class Pump_View():
    def __init__(self):
        """
        In this constructor, I create some QWidgets as placeholders until they get defined later.
        """
        self.LE_PumpName = qtw.QLineEdit()
        self.LE_FlowUnits = qtw.QLineEdit()
        self.LE_HeadUnits = qtw.QLineEdit()
        self.LE_HeadCoefs = qtw.QLineEdit()
        self.LE_EffCoefs = qtw.QLineEdit()
        self.ax = None
        self.canvas = None

    def updateView(self, Model):
        """
        Put model parameters in the widgets.
        :param Model:
        :return:
        """
        self.LE_PumpName.setText(Model.PumpName)
        self.LE_FlowUnits.setText(Model.FlowUnits)
        self.LE_HeadUnits.setText(Model.HeadUnits)
        self.LE_HeadCoefs.setText(Model.LSFitHead.GetCoeffsString())
        self.LE_EffCoefs.setText(Model.LSFitEff.GetCoeffsString())
        self.DoPlot(Model)

    def DoPlot(self, Model):
        """
        Create the plot.
        :param Model:
        :return:
        """
        headx, heady, headRSq = Model.LSFitHead.GetPlotInfo(3, npoints=500)
        effx, effy, effRSq = Model.LSFitEff.GetPlotInfo(3, npoints=500)

        axes = self.ax
        self.ax.clear()
        self.ax.plot(Model.FlowData, Model.HeadData, 'bo', label='Head Data')
        self.ax.plot(headx, heady, 'r-', label=f'Head Fit, R^2={headRSq:.2f}')
        self.ax.plot(Model.FlowData, Model.EffData, 'go', label='Efficiency Data')
        self.ax.plot(effx, effy, 'y-', label=f'Efficiency Fit, R^2={effRSq:.2f}')
        self.ax.set_xlabel(Model.FlowUnits)
        self.ax.set_ylabel(f"{Model.HeadUnits} and Efficiency (%)")
        self.ax.legend()
        self.ax.set_title('Pump Curve Analysis')
        self.canvas.draw()

    def setViewWidgets(self, w):
        self.LE_PumpName, self.LE_FlowUnits, self.LE_HeadUnits, self.LE_HeadCoefs, self.LE_EffCoefs, self.ax, self.canvas = w
# endregion