import unittest
import pyphy

class TestPyphy (unittest.TestCase):
	def test_TaxidToName(self):
		self.assertEqual(pyphy.getNameByTaxid(2), "Bacteria")

	def test_NameToTaxid(self):
		self.assertEqual(pyphy.getTaxidByName("Proteobacteria")[0], 1224)

	def test_getRankByName(self):
		self.assertEqual(pyphy.getRankByName("Proteobacteria"), "phylum")

	def test_getAllNameByTaxid(self):
		self.assertCountEqual(pyphy.getAllNameByTaxid(976), ['Bacteroidetes', 'Bacteroides-Cytophaga-Flexibacter group', 'BCF group', 'Bacteroidaeota', 'Bacteroidota', 'Cytophaga-Flexibacter-Bacteroides phylum', 'CFB group'])

	def test_getParentByName(self):
		self.assertEqual(pyphy.getParentByName("Bacteroidetes"), 68336)

	def test_getDictPathByTaxid(self):
		self.assertEqual(pyphy.getDictPathByTaxid(1224), {'phylum': 1224, 'superkingdom': 2, 'no rank': 1})

