"""Defines an Equivalent Circuit Battery Model"""

import numpy as np
import math

from battery import Battery
from metric import Charge
import config


class EquivalentCircuitBattery(Battery):
    """Battery class with an interface that can hook up to a tester for cycling."""

    def apply_potential(self, potential):
        """
        Charge or discharge the battery for one timestep by applying an external potential.

        Parameters
        ----------
        potential : float
            The external potential.  If the external potential is equal to the ocp from the
            previous timestep, and the battery is at equilibrium, there should be no resulting
            current.

        Returns
        -------
        ocp : float
            The battery open circuit potential after the timestep.
        timestep_current : float
            Charge transferred into in the battery during the timestep.  A positive current is
            an increase in the charge of the battery.
        """

