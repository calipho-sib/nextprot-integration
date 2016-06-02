from unittest import TestCase

from nextprot_integration.service.npdb import DatabaseService


class TestDatabaseService(TestCase):

    def test_db(self):
        DatabaseService.check_database("np_annot_uat")

    def test_db_not_found(self):
        """Should throw an OS error"""
        with self.assertRaises(ValueError):
            DatabaseService.check_database("np_annot_ua")

    def test_dump_db(self):
        DatabaseService.dump_db(db_name="np_annot_uat", db_schema="np_mappings", dump_dir="/tmp")

    def test_dump_db_failed_bad_db(self):
        with self.assertRaises(ValueError):
            DatabaseService.dump_db(db_name="np_annot_ua", db_schema="np_mappings", dump_dir="/tmp")

    def test_dump_db_failed_bad_schema(self):
        with self.assertRaises(ValueError):
            DatabaseService.dump_db(db_name="np_annot_uat", db_schema="np_mapping", dump_dir="/tmp")

    def test_dump_db_failed_unknown_dump_dir(self):
        with self.assertRaises(ValueError):
            DatabaseService.dump_db(db_name="np_annot_uat", db_schema="np_mappings", dump_dir="/temp")

    #def test_update_db_mappings(self):
    #    DatabaseService.update_db_schema(IntegrationWorkflow(dev_mode=True), "mappings")

    def test_exec_query(self):
        results = DatabaseService.exec_query("np_annot_uat", "SELECT t.* FROM nextprot.cv_status t")
        self.assertEqual(6, len(results))
        self.assertEqual((1, 'valid', 'valid sequence identifier'), results[0])
        self.assertEqual((2, 'obsolete', 'obsolete sequence identifier'), results[1])
        self.assertEqual((3, 'failed', 'failure of the db load'), results[2])
        self.assertEqual((4, 'excluded', 'data to exclude from nextprot'), results[3])
        self.assertEqual((5, 'RESOLVED', 'The issue has been resolved'), results[4])
        self.assertEqual((6, 'REVIEWED', 'The issue has been manually reviewed'), results[5])