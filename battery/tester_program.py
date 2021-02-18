"""Defines a test program (aka procedure, protocol)."""

from config import *


class TesterProgram:
    """Program."""

    charge_cv = CHARGE_CV
    """Voltage used for a constant-voltage charge step."""
    driver = DPOT_INIT
    """Driving potential."""
    timestep = 1
    """Current timestep of the entire program."""
    timesteps_in_step = 1
    """Number of timesteps taken in this program step so far."""
    step = "CHARGE_CC"
    """Step of the program."""

    def advance(self, battery, current, increment_timesteps=True):
        """Advance the test program one timestep.

        This is a CC/CV test: constant current for first part, then constant potential.

        Parameters
        ----------
        battery : Battery
        current : float
            Last current.
        increment_timesteps : bool
            Increment the timesteps if True.  This is to allow for setting False to switch steps.
            TODO: record timesteps (total and per-step) in the Tester, not the program?

        Returns
        -------
        target_current
        """
        step = self.step
        timesteps_in_step = self.timesteps_in_step
        # Increment timesteps
        if increment_timesteps:
            self.timestep += 1
            self.timesteps_in_step += 1

        pot = battery.ocp  # potential 1 tick in, not drive potential
        # pot = charge_y[0]  # drive potential
        if step == "CHARGE_CC":
            if pot >= CHARGE_CV:
                # Change phase.
                self.step = "CHARGE_CV"
                return self.advance(battery, current, increment_timesteps=False)
            else:
                target_current = CHARGE_CC
                self.driver = battery.get_driver_for_target_current(target_current)
        elif step == "CHARGE_CV":
            # Check if current is close to 0.
            if current < ZERO_CURRENT_THRESHOLD:
                # Change step.
                self.step = "REST"
                return self.advance(battery, current, increment_timesteps=False)
            else:
                target_pot = CHARGE_CV
                self.driver = battery.get_driver_for_target_ocp(target_pot)
        elif step == "REST":
            if timesteps_in_step > REST_TIMESTEPS:
                # Change step.
                self.step = "DISCHARGE_CC"
                return self.advance(battery, current, increment_timesteps=False)
            else:
                target_current = 0
                self.driver = battery.get_driver_for_target_current(target_current)
        elif step == "DISCHARGE_CC":
            if pot <= DISCHARGE_CV:
                # Change step.
                self.step = "DISCHARGE_CV"
                return self.advance(battery, current, increment_timesteps=False)
            else:
                target_current = -CHARGE_CC
                self.driver = battery.get_driver_for_target_current(target_current)
        elif step == "DISCHARGE_CV":
            # Check if current is close to 0.
            if current > -ZERO_CURRENT_THRESHOLD:
                # Change step back to beginning of new cycle.
                self.step ="CHARGE_CC"
                return self.advance(battery, current, increment_timesteps=False)
            else:
                target_pot = DISCHARGE_CV
                self.driver = battery.get_driver_for_target_ocp(target_pot)
        else:
            raise Exception("Unrecognized Test Step '%s'" % step)