"""Defines a Tester class to run tests on a battery."""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

import config
from battery import Battery
from tester_program import TesterProgram
from metric import Metrics, Charge, SOC, Current, Driver, Potential  # , Dqdv

plt.style.use('seaborn-pastel')


class TestRun:
    """An execution of a test program."""

    def __init__(self, battery, tester, program):
        """Constructor.

        Parameters
        ----------
        battery : Battery
        tester : Tester
        program : TestProgram
        """


class Tester:
    """Battery tester.  Runs a test program to cycle a battery."""

    def __init__(self, battery, program):
        """

        Parameters
        ----------
        battery : Battery
        program : TesterProgram
        """
        self.battery = battery
        self.program = program
        self.metrics = Metrics(
            Charge(Charge.get_init_vals()[0], battery.charge_curve), SOC(0, 0), Current(0, 0),
            Driver(0, 0), Potential(0, 0)  # , Dqdv(0, 0)
        )

    def setup_figure(self):
        """Create the figure and add plots."""
        fig = plt.figure(figsize=(12.80, 7.20))
        for metric in self.metrics:
            metric.add_subplot(fig)

        return fig

    def get_init(self):
        """Get the init function for animation."""
        def init():
            lines = [metric.init_plot() for metric in self.metrics]
            return lines
        return init

    def get_animate(self):
        """Get the animate function for animation."""
        def animate(frame):
            """Plot the metrics for an animation frame.

            Parameters
            ----------
            frame
                The next value in FuncAnimation.frames, passed in by matplotlib.
            """
            # Set frame data on each metric.  Incoming frame data must correspond to metric list.
            # frame = self.advance_timestep()
            xy_pairs = list(frame)
            lines = [metric.set_data(xy_pairs.pop(0)) for metric in self.metrics]
            return lines
        return animate

    def get_angle_boundary(self, y_intercept):
        """Get an angled boundary as a function of x."""
        def angle_boundary(x):
            return -x + y_intercept
        return angle_boundary

    def advance_timestep(self):
        """Advance the program one timestep forward, applying driving potential to the battery.

        Returns
        -------
        frame
        """
        battery, program, metrics = (self.battery, self.program, self.metrics)
        print("calc frame %s - %s" % (program.timestep, program.step))

        # Record the driver.
        metrics.driver.update(program.timestep, program.driver)

        # Apply potential to the battery for one timestep.
        battery.apply_potential(program.driver)

        # Get the new charge curve.
        metrics.charge.update(metrics.charge.x, battery.charge_curve)

        # Update metrics
        metrics.soc.update(program.timestep, np.sum(metrics.charge.y))
        metrics.influx.update(program.timestep, metrics.soc.delta())
        metrics.potential.update(program.timestep, metrics.charge.y[0])
        # metrics.dqdv.update(
        #     potential.val,
        #     metrics.soc.delta() / metrics.potential.delta() if phase == "CHARGE_CC" else 0
        # )

        # Get new phase and driver values.
        program.advance(battery, metrics.influx.get_val())

        # Append curves to frame list for plot animation.
        frame = [metric.get_xy_copy() for metric in metrics]  # can't be a generator for anim.
        return frame

    def generate_frames(self, num_timesteps):
        """Frame generator.

        Parameters
        ----------
        num_timesteps : int
            Number of frames generated; thus, number of program timesteps advanced.

        Returns
        -------
        frames : generator
            Generator of frames.
        """
        for _ in range(num_timesteps):
            frame = self.advance_timestep()
            yield frame

    def run_program(self, num_timesteps, do_animate=True, save=False):
        """Run the tester program for num_timesteps timesteps, rendering and optionally saving plot.

        Parameters
        ----------
        num_timesteps : int
            Number of timesteps to run.
        do_animate : bool
            If true, an animation will be shown.  If false, only the last frame will render.
        save : bool
            Save the animation.
        """

        # Initialize plots.
        fig = self.setup_figure()
        plot_init = self.get_init()

        # Render plots.
        if do_animate:
            # Animate plots.
            animate = self.get_animate()
            frames = self.generate_frames(num_timesteps)
            # noinspection PyTypeChecker
            anim = FuncAnimation(
                fig, animate, init_func=plot_init, frames=frames, interval=config.ANIM_INTERVAL,
                repeat=True, repeat_delay=1000, blit=True, save_count=num_timesteps
            )

            # Save animation or show snapshot.
            if save:
                print("Saving animation...")
                anim.save(config.ANIM_SAVE_FILE, writer='imagemagick', dpi=config.ANIM_DPI)
                print("Done.")
            else:
                plt.show()
        else:
            # Plot without animation.
            frame = None
            for i in range(num_timesteps):
                frame = self.advance_timestep()
            self.get_animate()(frame)
            plt.show()

    def run_one_timestep(self, program, battery, driver, t, phase, soc_y, influx_y, ):
        """Run a single timestep of the program."""

    def print_metrics(self, metrics):
        """Print values of metrics for debugging."""
        print(
            "new_y[0]: %s | soc: %s | influx: %s | driver: %s | potential: %s | dqdv: %s"
            % (
                metrics.charge[0], metrics.soc[-1], metrics.influx[-1],
                metrics.driver[-1], metrics.potential[-1], metrics.dqdv
            )
        )
