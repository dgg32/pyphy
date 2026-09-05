import unittest
import os
import pyphy

# Run against a small, frozen snapshot of real NCBI data (see
# build_test_fixture.py) instead of whatever ncbi.db a developer happens to
# have configured locally. NCBI revises the live taxonomy constantly --
# renamed ranks, renamed preferred names, new species -- so pinning the
# tests to a real but frozen snapshot is what keeps this suite deterministic
# and independent of a taxdmp download, rather than to a moving target.
pyphy.db = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_fixture.db')

class TestPyphy (unittest.TestCase):
	def test_TaxidToName(self):
		self.assertEqual(pyphy.getNameByTaxid(2), "Bacteria")

	def test_NameToTaxid(self):
		self.assertEqual(pyphy.getTaxidByName("Proteobacteria")[0], 1224)

	def test_getRankByName(self):
		self.assertEqual(pyphy.getRankByName("Proteobacteria"), "phylum")

	def test_getAllNameByTaxid(self):
		self.assertCountEqual(pyphy.getAllNameByTaxid(976), ['Bacteroidota', 'Sphingobacteria', 'Bacteroidetes', 'BCF group', 'Kapaibacteriota', 'CFB group', '"Bacteroidota" Whitman et al. 2018', 'Candidatus Kapaibacteriota'])

	def test_getParentByName(self):
		self.assertEqual(pyphy.getParentByName("Bacteroidetes"), 68336)

	def test_getDictPathByTaxid(self):
		self.assertEqual(pyphy.getDictPathByTaxid(1224), {'phylum': 1224, 'kingdom': 3379134, 'domain': 2, 'cellular root': 131567, 'no rank': 1})
		self.assertEqual(pyphy.getDictPathByTaxid("N/A"), {'no rank': -1})

	def test_getSonsByName(self):
		self.assertCountEqual(pyphy.getSonsByName("Leptospirillum"), [149699, 184209, 261385, 261386, 655606, 1260982, 2629551])

	def test_getAllSonsByTaxid(self):
		self.assertCountEqual(pyphy.getAllSonsByTaxid(2629551), [181, 90965, 90966, 90968, 133855, 133856, 133857, 196487, 392727, 502582, 511488, 511489, 694040, 948304, 948305, 948306, 948307, 948308, 948309, 1090554, 1402919, 1484337, 1502095, 1502778, 1572228, 1572229, 3682685])

if __name__ == '__main__':
	unittest.main()
