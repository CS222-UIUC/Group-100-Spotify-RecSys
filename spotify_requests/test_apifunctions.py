import unittest

from geniusapi import GetAPIObjects
from geniusapi import RecommendationsFromTops
from geniusapi import CommentsofRecommendations



class TestRecommendationAndComments(unittest.TestCase):
    def test_getAPI(self):
        """
        Test that function runs without error
        """
        try:
            genius, spotify = GetAPIObjects()
        except BaseException as exc:
            assert False, f'raised an exception {exc}'
    def test_recommendations(self):
        """
        Test that function runs without error
        """
        try:
            recs = RecommendationsFromTops()
        except BaseException as exc:
            assert False, f'raised an exception {exc}'
    def test_getComments(self):
        """
        Test that function only accepts list
        """
        data = 8
        with self.assertRaises(TypeError):
            result = CommentsofRecommendations(data)

if __name__ == '__main__':
    unittest.main()