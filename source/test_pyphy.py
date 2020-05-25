import unittest
import pyphy

class TestTaxidAndName (unittest.TestCase):
	def test_TaxidToName(self):
		self.assertEqual(pyphy.getNameByTaxid(2), "Bacteria")

	def test_NameToTaxid(self):
		self.assertEqual(pyphy.getTaxidByName("Proteobacteria")[0], 1224)