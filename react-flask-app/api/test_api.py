import time
import json
import unittest
from flask import Flask, jsonify, request
import api


class FlaskAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = api.app.test_client()
        cls.app.testing = True

    def test_get_current_time(self):
        response = self.app.get("/api/time")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("time", data)
        self.assertIsInstance(data["time"], float)

    def test_send_message(self):
        test_name = "Jane Doe"
        response = self.app.post(
            "/api/send-message",
            data=json.dumps({"name": test_name}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("responseMessage", data)

        self.assertEqual(data["responseMessage"], f"Hello {test_name}")


if __name__ == "__main__":
    unittest.main()
