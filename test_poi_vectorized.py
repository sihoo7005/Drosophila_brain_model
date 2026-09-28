import unittest

import numpy as np
from brian2 import Network, NeuronGroup, PoissonInput, defaultclock, ms, prefs

from model import default_params, poi


class VectorizedPoissonInputTests(unittest.TestCase):
    def test_event_counts_match_poissoninput_distribution(self):
        prefs.codegen.target = "numpy"
        n_targets = 128
        duration = 100 * ms
        rate = default_params["r_poi"]
        weight = default_params["w_syn"] * default_params["f_poi"]
        p = float(rate * defaultclock.dt)
        n_steps = int(duration / defaultclock.dt)
        expected_mean = n_steps * p
        standard_error = (n_steps * p * (1 - p) / n_targets) ** 0.5

        def run(vectorized):
            neurons = NeuronGroup(n_targets, "v : volt\nrfc : second")
            if vectorized:
                operations, _ = poi(neurons, range(n_targets), [], default_params)
                self.assertEqual(len(operations), 1)
            else:
                operations = [
                    PoissonInput(neurons[i], "v", N=1, rate=rate, weight=weight)
                    for i in range(n_targets)
                ]
            Network(neurons, *operations).run(duration)
            return np.asarray(neurons.v / weight)

        np.random.seed(783)
        legacy_counts = run(vectorized=False)
        np.random.seed(984)
        vectorized_counts = run(vectorized=True)

        for counts in (legacy_counts, vectorized_counts):
            self.assertLess(abs(counts.mean() - expected_mean), 5 * standard_error)


if __name__ == "__main__":
    unittest.main()
