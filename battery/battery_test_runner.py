"""
Script to run a test on a battery.

Usage:
python battery_test_runner.py
"""

from tester import Tester
from tester_program import TesterProgram
from diffusion_battery import DiffusionBattery
import config


def run():
    battery = DiffusionBattery()
    program = TesterProgram()
    tester = Tester(battery, program)

    tester.run_program(config.NUM_TIMESTEPS, do_animate=config.DO_ANIMATE, save=config.SAVE_ANIMATION)

run()
