"""Config settings for Battery, Tester, and Visualization."""

# TODO: take these out of the global namespace where possible

# Program params
NUM_TIMESTEPS = 750
DO_ANIMATE = True
SAVE_ANIMATION = True
ANIM_DPI = 70
ANIM_INTERVAL = 20
CHARGE_CC = 15
CHARGE_CV = 4
DISCHARGE_CV = 0
ZERO_CURRENT_THRESHOLD = 1
REST_TIMESTEPS = 20
DPOT_INIT = 0

# Battery params
N = 1000  # Number of points along X axis

# Animation save location
ANIM_SAVE_FILE = '/Users/fayvorlove/Documents/fayvor-sim-gifs/diffusion.gif'
