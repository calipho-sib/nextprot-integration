import os
from unittest import TestCase

from nextprot_integration.JavaPropertyMap import JavaPropertyMap


class TestJavaPropertyMap(TestCase):

    prop_file = os.getcwd()+"/dataload.properties"
    another_prop_file = os.getcwd()+"/another.properties"

    def setUp(self):
        pass

    def test_constr(self):
        """Is constructor fine?"""
        JavaPropertyMap(self.__class__.prop_file)

    def test_constr_missing_file(self):
        """Should throw an IO error"""
        with self.assertRaises(IOError):
            self.assertRaises(IOError, JavaPropertyMap("file.properties"))

    def test_constr_empty_file(self):
        """Should throw an IO error"""
        with self.assertRaises(IOError):
            self.assertRaises(IOError, JavaPropertyMap("dataload-empty.properties"))

    def test_get_property(self):
        prop = JavaPropertyMap(self.__class__.prop_file)
        self.assertEqual('/Users/spongebob/data/integration', prop.get_property("integration.dir"))
        self.assertEqual('/Users/spongebob/data/integration/log', prop.get_property("integration.log.dir"))
        self.assertEqual('2016_04', prop.get_property("uniprot.release"))
        self.assertEqual('84', prop.get_property("ensembl.release"))
        self.assertEqual('/Users/spongebob/data/integration/dump/2016_04', prop.get_property("database.dump.dir"))
        self.assertEqual('/Users/spongebob/Projects/proto/integration/export', prop.get_property("export.dir"))
        self.assertEqual('/Users/spongebob/Projects/proto/integration/export/cvterms.txt', prop.get_property("cvterms.output.filename"))
        self.assertEqual('/Users/spongebob/Projects/proto/integration/export/cvmappings.txt', prop.get_property("cvmappings.output.filename"))
        self.assertEqual('/Users/spongebob/Projects/proto/integration/export/cvdatabases.txt', prop.get_property("cvdatabases.output.filename"))

    def test_get_property_from_non_curly_props(self):
        prop = JavaPropertyMap(os.getcwd() + "/dataload-no-curly.properties")
        self.assertEqual('/Users/spongebob/data/integration', prop.get_property("integration.dir"))
        self.assertEqual('/Users/spongebob/data/integration/log', prop.get_property("integration.log.dir"))
        self.assertEqual('2016_04', prop.get_property("uniprot.release"))
        self.assertEqual('84', prop.get_property("ensembl.release"))
        self.assertEqual('/Users/spongebob/data/integration/dump/2016_04', prop.get_property("database.dump.dir"))
        self.assertEqual('/Users/spongebob/Projects/proto/integration/export', prop.get_property("export.dir"))
        self.assertEqual('/Users/spongebob/Projects/proto/integration/export/cvterms.txt', prop.get_property("cvterms.output.filename"))
        self.assertEqual('/Users/spongebob/Projects/proto/integration/export/cvmappings.txt', prop.get_property("cvmappings.output.filename"))
        self.assertEqual('/Users/spongebob/Projects/proto/integration/export/cvdatabases.txt', prop.get_property("cvdatabases.output.filename"))

    def test_get_property_none(self):
        prop = JavaPropertyMap(self.__class__.prop_file)
        self.assertEqual(None, prop.get_property("ensembl.releas"))

    def test_count_properties(self):
        prop = JavaPropertyMap(self.__class__.prop_file)
        self.assertEqual(9, prop.count_properties())

    def test_add_property(self):
        prop = JavaPropertyMap(self.__class__.prop_file)
        prop.add_property("bob", "sponge")
        self.assertEqual(10, prop.count_properties())
        self.assertEqual("sponge", prop.get_property("bob"))

    def test_load_another_property_file(self):
        prop = JavaPropertyMap(self.__class__.prop_file)
        prop.load_properties(self.__class__.another_prop_file)
        self.assertEqual('/Users/spongebob/data/integration/build/jars', prop.get_property("jar.repository.path"))
