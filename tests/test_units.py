from app import app
from unittest import TestCase
from bs4 import BeautifulSoup


class TestPost(TestCase):
    """ This tests tries to post data to the endpoint """
    def setUp(self):
        self.app = app
        self.app.debug = True
        self.client = self.app.test_client()

    def open_read(self, filepath: str):
        with open(filepath) as f:
            xml_data = f.read()
        return xml_data

    def post(self, data, data_type):
        request = self.client.post("/analysis", data={
            "resource_type": data_type,
            "resource": data
        })
        return BeautifulSoup(request.data.decode(), "lxml")

    def assertPassed(self, data, status: bool=True):
        if status:
            status = "Passed"
        else:
            status = "Failed"
        self.assertEqual(
            data.select("#general_status")[0].text, status
        )

    def test_textgroup_valid(self):
        """ Check that a valid textgroup passes """
        data = self.post(self.open_read("tests/data/textgroup_valid.xml"), "cts_metadata")
        self.assertPassed(data)

    def test_textgroup_invalid(self):
        """ Check that an invalid textgroup fails """
        data = self.post(self.open_read("tests/data/textgroup_invalid.xml"), "cts_metadata")
        self.assertPassed(data, False)

    def test_epidoc_valid(self):
        """ Check that a valid epidoc text passes """
        data = self.post(self.open_read("tests/data/epidoc_valid.xml"), "cts_epidoc")
        self.assertPassed(data)
