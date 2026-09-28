import unittest

from neuron_lookup import get_neurons


class NeuronLookupTests(unittest.TestCase):
    def test_known_cell_types_return_sorted_model_ids(self):
        for cell_type in ("L1", "L2", "T3"):
            neurons = get_neurons(cell_type)
            self.assertTrue(neurons)
            self.assertEqual(neurons, sorted(neurons))
            self.assertTrue(all(isinstance(neuron_id, int) for neuron_id in neurons))

    def test_lookup_is_exact(self):
        self.assertEqual(get_neurons(" l1 "), get_neurons("L1"))
        with self.assertRaises(ValueError):
            get_neurons("L")

    def test_unknown_cell_type_is_explicit(self):
        with self.assertRaisesRegex(ValueError, "Unknown cell type"):
            get_neurons("not-a-real-cell-type")


if __name__ == "__main__":
    unittest.main()
