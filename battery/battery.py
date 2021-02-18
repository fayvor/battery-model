"""Defines a Battery Class"""

import numpy as np


class Battery:

    def __init__(self, soc=0, ocp=0, charge_curve=np.array([])):
        """

        Parameters
        ----------
        soc : float
            The quantity of charge in the battery.
        ocp : float
            The open-circuit potential of the battery.
        charge_curve : np.array
            An internal view of the charge across the thickness of the cathode.  Some models may
            not maintain this data.
        """
        self.soc = soc
        self.ocp = ocp
        self.charge_curve = charge_curve

    def apply_potential(self, potential):
        """Apply external potential.

        Parameters
        ----------
        potential : float
            External potential applied at the beginning of the timestep.

        Returns
        -------
        ocp : float
            The battery open circuit potential after the timestep.
        timestep_current : float
            Charge transferred into in the battery during the timestep.  A positive current is
            an increase in the charge of the battery.
        """


class Anode:
    """Negative electrode of the battery."""


class Cathode:
    """Positive electrode of the battery."""


class Separator:
    """Separator between battery electrodes."""
