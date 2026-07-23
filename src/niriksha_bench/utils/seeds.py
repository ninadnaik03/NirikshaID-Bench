import random

import numpy as np


def seeded(seed: int) -> tuple[random.Random, np.random.Generator]:
    return random.Random(seed), np.random.default_rng(seed)

