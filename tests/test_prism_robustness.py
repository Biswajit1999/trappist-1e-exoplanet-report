import unittest
import numpy as np
from scripts.prism_robustness import ar1_covariance, gls_flatness, leave_one_bin_out


class TestPrismRobustness(unittest.TestCase):
    def test_ar1(self):
        c = ar1_covariance([2., 3., 4.], 0.5)
        self.assertAlmostEqual(c[0, 2], 2.0)
        self.assertTrue(np.all(np.linalg.eigvalsh(c) > 0))

    def test_gls_diagonal(self):
        mean, err, chi2 = gls_flatness([2., 4., 6.], np.eye(3))
        self.assertAlmostEqual(mean, 4.)
        self.assertAlmostEqual(err, 1 / np.sqrt(3))
        self.assertAlmostEqual(chi2, 8.)

    def test_correlated_constant(self):
        c = ar1_covariance([1., 1., 1., 1.], 0.7)
        mean, err, chi2 = gls_flatness([3.] * 4, c)
        self.assertAlmostEqual(mean, 3.)
        self.assertAlmostEqual(chi2, 0.)
        self.assertGreater(err, 0.5)

    def test_deletion_matches_refit(self):
        y = np.array([2., 4., 8., 3.])
        s = np.array([1., 2., 1., 3.])
        full, delta = leave_one_bin_out(y, s)
        for i in range(len(y)):
            mask = np.arange(len(y)) != i
            w = 1 / s[mask]**2
            expected = np.dot(w, y[mask]) / sum(w)
            self.assertAlmostEqual(full + delta[i], expected)

    def test_invalid_covariance(self):
        with self.assertRaises(np.linalg.LinAlgError):
            gls_flatness([1., 2.], [[1., 2.], [2., 1.]])


if __name__ == "__main__":
    unittest.main()
