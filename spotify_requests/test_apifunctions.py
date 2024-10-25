import unittest

from geniusapi import GetAPIObjects, RecommendationsFromTops, CommentsofRecommendations, GetAccessTokenWithAuthorization
import warnings

class TestRecommendationAndComments(unittest.TestCase):

    def test_getAccessTokenWithAuthorization(self):
        """
        Test that function runs without error
        """
        try:
            GetAccessTokenWithAuthorization()
        except BaseException as exc:
            assert False, f'raised an exception {exc}'
    def test_getAPI(self):
        """
        Test that function runs without error
        """
        try:
            token = GetAccessTokenWithAuthorization()
            spot, gen = GetAPIObjects(token)
        except BaseException as exc:
            assert False, f'raised an exception {exc}'
    def test_recommendations(self):
        """
        Test that function runs without error
        """
        try:
            RecommendationsFromTops()
        except BaseException as exc:
            assert False, f'raised an exception {exc}'
    def test_CommentsWeirdInput(self):
        """
        Test that function only accepts list
        """
        data = 8
        with self.assertRaises(TypeError):
            CommentsofRecommendations(data)
    
    def test_CommentsStrInput(self):
        """
        Test that function only accepts list
        """
        data = "RipTide"
        with self.assertRaises(TypeError):
            CommentsofRecommendations(data)

    def test_CommentsNoSong(self):
        """
        Test that function only accepts list
        """
        data = ["i6ri8buy"]
        result = CommentsofRecommendations(data)
        self.assertEqual(result, "song not found")

if __name__ == '__main__':
    warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
    unittest.main()
