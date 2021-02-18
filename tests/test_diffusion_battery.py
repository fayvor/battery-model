"""Tests of the Diffusion Battery model."""

import pytest
import numpy as np

from battery.diffusion_battery import DiffusionBattery


@pytest.skip()
def test_impulse_diffusion():
    """Apply potential for one step and test diffusion."""
    bat = DiffusionBattery()
    bat.cathode_width = 3


def test_get_driver_for_target_current():
    """Test calculation of external potential needed to achieve target current."""
    bat = DiffusionBattery()
    bat.cathode_width = 3
    bat.charge_curve = np.array([1, 2, 3])
    target_ocp = 2
    drive_pot = bat.get_driver_for_target_ocp(target_ocp)

    # Make projection; this should be close to target_val
    projected_ocp = bat.get_calc_ocp(bat.charge_curve)(drive_pot)
    assert round(float(target_ocp), 8) == round(projected_ocp, 8)

