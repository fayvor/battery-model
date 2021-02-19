"""Defines a Diffusion Battery Model"""

import numpy as np
import math

from .battery import Battery
from .metric import Charge
from . import config


class DiffusionBattery(Battery):
    """Battery class with an interface that can hook up to a tester for cycling."""

    def __init__(self, soc=0, ocp=0, charge_curve=Charge.get_init_vals()[1], cathode_width=config.N):
        """

        Parameters
        ----------
        soc
            The quantity of charge in the battery.
        ocp
        charge_curve
        cathode_width
        """
        super(DiffusionBattery, self).__init__(soc, ocp, charge_curve)
        self.cathode_width = cathode_width

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
        # Get the new charge distribution given the external potential
        new_charge_curve = self.compute_charge_curve(potential, self.charge_curve)

        # Set the battery state.
        self.charge_curve = new_charge_curve
        self.ocp = new_charge_curve[1]
        prior_soc = self.soc
        self.soc = self.charge_curve.sum()
        timestep_current = self.soc - prior_soc
        return self.ocp, timestep_current

    def compute_charge_curve(self, drive_pot, charge_curve):
        """Get charge distribution.

        Use Fick's second law to determine the concentration at time t and point x
        https://en.wikipedia.org/wiki/Fick%27s_laws_of_diffusion

        Using the example solution in one dimension:
        https://en.wikipedia.org/wiki/Fick%27s_laws_of_diffusion#Example_solution_in_one_dimension:_diffusion_length

        Parameters
        ----------
        drive_pot : float
            The driving potential.
        charge_curve : numpy.array
            The charge distribution in the cathode.

        Returns
        -------
        numpy.array
        """
        y = charge_curve.copy()  # Make a copy so we still have access to the original.
        y[0] = drive_pot
        sigma = self.cathode_width / 10  # keep this above 2 * width + 1 to ensure the gaussian fits
        dx = float(1)
        width = 3
        # Make a symmetrical array
        gx = np.arange(-width * sigma, width * sigma + 1, dx)
        # Make a normal distribution for which the area under the curve is 1.
        gaussian = np.exp(-(gx ** 2) / (2 * sigma ** 2)) / math.sqrt(2 * math.pi * sigma ** 2)
        # Ensure area under the curve is 1, given that the tails are getting cut off.
        gaussian = gaussian / np.sum(gaussian)
        zeros = np.array([0 for val in gaussian])
        prepend = np.array([y[0] for val in gaussian])
        # Prepend and strip an array of repeated values.  Append a flipped (mirror) copy as a wall.
        base = np.concatenate((zeros, prepend, y, np.flip(y)))
        pad_len = 2 * len(gaussian)
        # Convolve the charge function with the Gaussian.
        convolution = np.convolve(base, gaussian, mode="same")
        # Trim off the extra data on the ends.
        new_charge_curve = convolution[pad_len:-len(y)]
        return new_charge_curve

    def compute_current(self, drive_pot, charge_curve):
        """Get current by running a timestep computation on charge_curve."""
        return np.sum(self.compute_charge_curve(drive_pot, charge_curve)) - np.sum(charge_curve)

    def compute_ocp(self, drive_pot, charge_curve):
        """Get open circuit potential by running a timestep computation on charge_curve."""
        return self.compute_charge_curve(drive_pot, charge_curve)[0]

    def get_calc_current(self, charge_curve):
        """Get function calc_current."""

        def calc_current(drive_pot):
            """Calculate current given drive potential."""
            new_charge_curve = charge_curve.copy()
            new_charge_curve[0] = drive_pot
            return self.compute_current(drive_pot, new_charge_curve)

        return calc_current

    def get_calc_ocp(self, charge_curve):
        """Get function calc_ocp."""

        def calc_ocp(drive_pot):
            """Calculate open circuit potential given drive potential."""
            new_charge_curve = charge_curve.copy()
            new_charge_curve[0] = drive_pot
            return self.compute_ocp(drive_pot, new_charge_curve)

        return calc_ocp

    def get_driver_for_target_current(self, target_influx):
        """Calculate drive_pot to produce the target current from charge_y."""
        return self.guess_drive_pot(
            self.charge_curve, self.compute_current, self.get_calc_current, target_influx
        )

    def get_driver_for_target_ocp(self, target_ocp):
        """Calculate new_drive_pot to produce the target_pot from charge_y.

        Parameters
        ----------
        target_ocp :

        Returns
        -------
        drive_pot : float
            The drive potential that is needed to result in the target_ocp after a timestep.
        """
        return self.guess_drive_pot(
            self.charge_curve, self.compute_ocp, self.get_calc_ocp, target_ocp
        )

    def guess_drive_pot(
            self, charge_curve, get_val_from_charge_curve, get_val_from_charge_curve_and_drive_pot,
            target_val
    ):
        """

        Parameters
        ----------
        charge_curve
            The charge curve of the cathode.
        get_val_from_charge_curve : function
            Potential or Current as a function of the charge curve.
        get_val_from_charge_curve_and_drive_pot
            Potential or Current as a function of the charge curve and the drive potential.
        target_val
            Target Potential or Current.

        Returns
        -------

        """
        drive_pot = charge_curve[0]
        # Compute actual_val expected with no changes.
        actual_val = get_val_from_charge_curve(drive_pot, charge_curve)

        if actual_val == target_val:
            # No adjustment to drive potential is needed
            return drive_pot
        else:
            # Find new drive potential
            point1 = (actual_val, drive_pot)
            # Ensure they are paired.
            assert actual_val == get_val_from_charge_curve_and_drive_pot(charge_curve)(drive_pot)

            # Make a first guess based on fixed offset
            guess_drive_pot = drive_pot + 1
            guess_charge_y = charge_curve.copy()
            guess_charge_y[0] = guess_drive_pot
            guess_val = get_val_from_charge_curve(guess_drive_pot, guess_charge_y)
            point2 = (guess_val, guess_drive_pot)

            # Assume linear relationship between drive_pot and actual_val; get slope and intercept.
            slope, intercept = get_slope_intercept(point1, point2)
            guess_drive_pot_fin = (slope * target_val) + intercept

            return guess_drive_pot_fin


def get_slope_intercept(pt1, pt2):
    """Assuming a linear function through (x, y) pt1 and pt2, find the slope and y-intercept."""
    if pt1[0] - pt2[0] == 0:
        raise ZeroDivisionError
    slope = (pt1[1] - pt2[1]) / (pt1[0] - pt2[0])
    intercept = pt1[1] - slope * pt1[0]
    return slope, intercept


class Anode:
    """Negative electrode of the battery."""


class Cathode:
    """Positive electrode of the battery."""


class Separator:
    """Separator between battery electrodes."""
