import unittest

from geniusapi import GetAPIObjects, RecommendationsFromTops, CommentsofRecommendations, GetAccessTokenWithAuthorization, InfoOfRecommendations, RecommendationsFromParams
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
            GetAPIObjects(token)
        except BaseException as exc:
            assert False, f'raised an exception {exc}'
    def test_recommendations(self):
        """
        Test that function runs without error
        """
        try:
            recs = RecommendationsFromTops()
            for i in range(len(recs)):
                print(recs[i])
        except BaseException as exc:
            assert False, f'raised an exception {exc}'
    def test_CommentsWeirdInput(self):
        """
        Test that function only accepts list
        """
        data = 8
        with self.assertRaises(TypeError):
            CommentsofRecommendations(data, data)
    
    def test_CommentsStrInput(self):
        """
        Test that function only accepts list
        """
        data = "RipTide"
        with self.assertRaises(TypeError):
            CommentsofRecommendations(data, data)

    def test_CommentsNoSong(self):
        """
        Test if song isnt real
        """
        data = ["i6ri8buy"]
        result = CommentsofRecommendations(data, data)
        self.assertEqual(result, "song not found")
    
    def test_InfoWeirdInput(self):
        """
        Test that function only accepts list
        """
        data = 8
        with self.assertRaises(TypeError):
            InfoOfRecommendations(data, data)
    
    def test_InfoStrInput(self):
        """
        Test that function only accepts list
        """
        data = "RipTide"
        with self.assertRaises(TypeError):
            InfoOfRecommendations(data, data)

    def test_InfoNoSong(self):
        """
        Test if song isnt real
        """
        data = ["i6ri8buy"]
        result = InfoOfRecommendations(data,data)
        self.assertEqual(result, "song not found")
    
    def test_badDanceability(self):
        """
        Test function handles bad danceability input
        """
        genres = ['french','pop','r-n-b']
        danceability = 1.4
        popularity = 30
        tempo = 100
        result = RecommendationsFromParams(genres, danceability, popularity, tempo)
        self.assertEqual(result, "invalid danceabliity")
    
    def test_badPopularity(self):
        """
        Test function handles bad popularity input
        """
        genres = ['french','pop','r-n-b']
        danceability = .8
        popularity = 300
        tempo = 100
        result = RecommendationsFromParams(genres, danceability, popularity, tempo)
        self.assertEqual(result, "invalid popularity")
    
    def test_badTempo(self):
        """
        Test function handles bad tempo input
        """
        genres = ['french','pop','r-n-b']
        danceability = .8
        popularity = 30
        tempo = 1000
        result = RecommendationsFromParams(genres, danceability, popularity, tempo)
        self.assertEqual(result, "invalid tempo")

if __name__ == '__main__':
    warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
    unittest.main()
