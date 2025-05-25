import unittest
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from leaderboard import Leaderboard, Score # Assuming Score is also in leaderboard.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB_URL = 'sqlite:///./test_leaderboard.db'

class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        """Set up a temporary database for testing."""
        self.engine = create_engine(TEST_DB_URL)
        Score.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # Correctly pass the db_name, not the full URL
        self.leaderboard = Leaderboard(db_name='test_leaderboard.db')
        # Ensure the session used by Leaderboard is the test session
        self.leaderboard.Session = Session 

    def tearDown(self):
        """Clean up the temporary database."""
        self.session.close()
        
        # Drop tables using the test's primary engine
        # This needs to happen before the engine is disposed.
        Score.metadata.drop_all(self.engine) 
        
        # Dispose of the Leaderboard's internal engine
        # This is crucial to release its lock on the database file.
        if hasattr(self.leaderboard, 'engine') and self.leaderboard.engine is not None:
            self.leaderboard.engine.dispose()
            
        # Dispose of the test's primary engine
        self.engine.dispose()
        
        # Now it should be safe to remove the file
        db_file_path = 'test_leaderboard.db'
        if os.path.exists(db_file_path):
            try:
                os.remove(db_file_path)
            except OSError as e:
                # Optionally, print a warning if removal still fails, for debugging
                print(f"Warning: Could not remove test database {db_file_path}: {e}")

    def test_add_score(self):
        """Test adding a score to the leaderboard."""
        self.leaderboard.add_score('Player1', 100)
        scores = self.leaderboard.get_top_scores()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0][0], 'Player1') # Access by index
        self.assertEqual(scores[0][1], 100)     # Access by index

    def test_get_top_scores_empty(self):
        """Test getting top scores when the leaderboard is empty."""
        scores = self.leaderboard.get_top_scores()
        self.assertEqual(len(scores), 0)

    def test_get_top_scores_limit(self):
        """Test that get_top_scores returns the correct number of scores (default 10)."""
        for i in range(15):
            self.leaderboard.add_score(f'Player{i}', i * 10)
        scores = self.leaderboard.get_top_scores()
        self.assertEqual(len(scores), 10)
        self.assertEqual(scores[0][1], 140) # Highest score

    def test_get_top_scores_custom_limit(self):
        """Test get_top_scores with a custom limit."""
        for i in range(5):
            self.leaderboard.add_score(f'Player{i}', i * 10)
        scores = self.leaderboard.get_top_scores(count=3) # Changed limit to count
        self.assertEqual(len(scores), 3)
        self.assertEqual(scores[0][1], 40) # Highest score among the 5

if __name__ == '__main__':
    unittest.main()
