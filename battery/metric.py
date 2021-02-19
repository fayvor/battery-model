
import numpy as np
from collections import namedtuple

from .config import *

# Display params
PLOT_ROWS = 2
PLOT_COLS = 3

Metrics = namedtuple('Metrics', ['charge', 'soc', 'influx', 'driver', 'potential'])


class Metric:

    line = None

    @classmethod
    def add_subplot(cls, fig):
        """

        Parameters
        ----------
        fig : plt.Figure
        """
        pass

    @classmethod
    def init_plot(cls):
        x, y = ([], [])
        cls.line.set_data(x, y)
        return cls.line

    @classmethod
    def set_data(cls, xy):
        cls.line.set_data(xy[0], xy[1])
        return cls.line

    def __init__(self, x, y):
        """Initialize history."""
        self.x = np.array([x])
        self.y = np.array([y])

    def update(self, x_val, y_val):
        """Update the current value and history."""
        self.x = np.append(self.x, x_val)
        self.y = np.append(self.y, y_val)

    def get_val(self):
        return self.y[-1]

    def get_xy_copy(self):
        return self.x.copy(), self.y.copy()

    def delta(self):
        """Get the change from the previous value to the current value."""
        return self.y[-1] - self.y[-2]


class Charge(Metric):
    """The charge curve inside a battery.  This is really a feature of the battery and can't be
    measured directly by the tester.  But we have access to it from the simulation."""
    @classmethod
    def add_subplot(cls, fig):
        cls.axis = fig.add_subplot(1, PLOT_COLS, 1, label="xy", xlim=(0, N), ylim=(0, CHARGE_CV + 1))
        cls.axis.title.set_text('Charge over Distance')
        cls.line, = cls.axis.plot([], [], lw=3)
        return cls.line

    def __init__(self, x, y):
        """Initialize history."""
        self.x = np.array(x)
        self.y = np.array(y)

    @classmethod
    def get_init_vals(cls):
        x = np.array(range(N))
        y = np.array([0 for val in x])
        return x, y

    @classmethod
    def init_plot(cls):
        x, y = cls.get_init_vals()
        cls.line.set_data(x, y)
        return cls.line

    def update(self, x_val, y_val):
        """Update the current value and history."""
        self.x = x_val
        self.y = y_val


class Current(Metric):
    """Current into the battery during a timestep."""
    @classmethod
    def add_subplot(cls, fig):
        cls.axis = fig.add_subplot(PLOT_ROWS, PLOT_COLS, 2, label="influx", xlim=(0, NUM_TIMESTEPS), ylim=(-18, 18))
        cls.axis.title.set_text('Current')
        cls.line, = cls.axis.plot([], [], lw=3)


class SOC(Metric):
    """Charge in the battery."""
    @classmethod
    def add_subplot(cls, fig):
        cls.axis = fig.add_subplot(PLOT_ROWS, PLOT_COLS, 3, label="soc", xlim=(0, NUM_TIMESTEPS), ylim=(-2, 6000))
        cls.axis.title.set_text('Total Charge')
        cls.line, = cls.axis.plot([], [], lw=3)


class Potential(Metric):
    """Open circuit potential of the battery."""
    @classmethod
    def add_subplot(cls, fig):
        cls.axis = fig.add_subplot(PLOT_ROWS, PLOT_COLS, 5, label="potential", xlim=(0, NUM_TIMESTEPS), ylim=(-0.1, 5))
        cls.axis.title.set_text('Potential')
        cls.line, = cls.axis.plot([], [], lw=3)


class Driver(Metric):
    """Driving potential used by the tester to achieve the targets in the program."""
    @classmethod
    def add_subplot(cls, fig):
        cls.axis = fig.add_subplot(PLOT_ROWS, PLOT_COLS, 6, label="driver", xlim=(0, NUM_TIMESTEPS), ylim=(-0.5, 5))
        cls.axis.title.set_text('Driving Potential')
        cls.line, = cls.axis.plot([], [], lw=3)


class Dqdv(Metric):
    """Change in charge over the change in voltage in a given timestep.  This is an indicator of how
    easy it is to get charge into the battery (the higher the dQdV, the less energy needed per unit
    charge).
    """
    @classmethod
    def add_subplot(cls, fig):
        cls.axis = fig.add_subplot(PLOT_ROWS, 2, 6, label="dqdv", xlim=(-1, CHARGE_CV + 1), ylim=(-1000, 1000))
        cls.axis.title.set_text('dQ/dV over V')
        cls.line = cls.axis.scatter([], [], s=2)  # actually this is a PathCollection

    @classmethod
    def init_plot(cls):
        cls.line.set_offsets([])  # change the dots
        return cls.line

    @classmethod
    def set_data(cls, xy):
        cls.line.set_offsets(np.array(list(zip(xy[0], xy[1]))))  # change dots
        return cls.line
