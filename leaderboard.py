import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, desc, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Define the base for declarative models
Base = declarative_base()

class Score(Base):
    """SQLAlchemy model for the scores table."""
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Score(name='{self.name}', score={self.score}, timestamp='{self.timestamp}')>"

class Leaderboard:
    def __init__(self, db_name="leaderboard.db"):
        """
        Initializes the Leaderboard, setting up the SQLAlchemy engine and session.
        It also ensures the 'scores' table is created.

        Args:
            db_name (str): The name of the SQLite database file.
        """
        db_url = f"sqlite:///{db_name}"
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine) # Creates table if it doesn't exist
        self.Session = sessionmaker(bind=self.engine)

    def add_score(self, name, score):
        """
        Adds a new score to the leaderboard using SQLAlchemy.

        Args:
            name (str): The name of the player.
            score (int): The score achieved by the player.
        """
        if not isinstance(name, str) or not name.strip():
            print("Error: Player name must be a non-empty string.")
            return
        if not isinstance(score, int):
            print("Error: Score must be an integer.")
            return

        session = self.Session()
        try:
            new_score = Score(name=name, score=score)
            session.add(new_score)
            session.commit()
            print(f"Score added for {name}: {score}")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error while adding score: {e}")
        finally:
            session.close()

    def get_top_scores(self, count=10):
        """
        Retrieves the top N scores from the leaderboard using SQLAlchemy.

        Args:
            count (int): The number of top scores to retrieve.

        Returns:
            list: A list of Score objects (or dictionaries/tuples if processed).
                  Returns an empty list if no scores or an error occurs.
        """
        if not isinstance(count, int) or count <= 0:
            print("Error: Count must be a positive integer.")
            return []

        session = self.Session()
        try:
            # Querying Score objects directly
            top_scores_objects = session.query(Score).order_by(desc(Score.score), asc(Score.timestamp)).limit(count).all()
            # You can return the objects directly or process them into tuples/dictionaries as before
            return [(s.name, s.score, s.timestamp) for s in top_scores_objects]
        except SQLAlchemyError as e:
            print(f"Database error while fetching top scores: {e}")
            return []
        finally:
            session.close()

# Example Usage (optional - for testing the class directly)
if __name__ == '__main__':
    # Use a different DB name for SQLAlchemy testing to avoid conflicts if old DB exists
    leaderboard = Leaderboard(db_name="test_leaderboard_sqlalchemy.db")

    leaderboard.add_score("Player1_SQLA", 100)
    leaderboard.add_score("Player2_SQLA", 200)
    leaderboard.add_score("Player3_SQLA", 150)
    leaderboard.add_score("Player4_SQLA", 200) # Same score as Player2, older timestamp if Player2 added first

    print("\nTop Scores (SQLAlchemy):")
    top_scores = leaderboard.get_top_scores(5)
    if top_scores:
        for i, (name, score_val, ts) in enumerate(top_scores): # Renamed score to score_val to avoid conflict
            print(f"{i+1}. {name}: {score_val} (Achieved on: {ts})")
    else:
        print("No scores to display or error fetching scores.")

    leaderboard.add_score("Player5_SQLA", 300)
    leaderboard.add_score("Player6_SQLA", 50)
    
    print("\nTop Scores after more additions (SQLAlchemy):")
    top_scores = leaderboard.get_top_scores(3)
    if top_scores:
        for i, (name, score_val, ts) in enumerate(top_scores): # Renamed score to score_val
            print(f"{i+1}. {name}: {score_val} (Achieved on: {ts})")
    else:
        print("No scores to display or error fetching scores.")
        
    # Test edge cases for add_score
    leaderboard.add_score("", 100) # Empty name
    leaderboard.add_score("ValidName_SQLA", "not_an_int") # Invalid score type
    
    # Test edge cases for get_top_scores
    print("\nTop Scores with invalid count (SQLAlchemy):")
    leaderboard.get_top_scores(0)
    leaderboard.get_top_scores(-1)
    leaderboard.get_top_scores("abc")

    print("\nFetching all scores (e.g., top 100) (SQLAlchemy):")
    all_scores = leaderboard.get_top_scores(100)
    if all_scores:
        for i, (name, score_val, ts) in enumerate(all_scores): # Renamed score to score_val
            print(f"{i+1}. {name}: {score_val} (Achieved on: {ts})")
    else:
        print("No scores to display or error fetching scores.")
