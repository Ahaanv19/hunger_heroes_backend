"""
Hunger Heroes Game Leaderboard Model

Table: hunger_heroes_leaderboard

Tracks scores from the Hunger Heroes food bank exploration game (GameEngine v1.1).
Players walk around a food bank, interact with NPCs, and learn about the donation system.

Score formula:
  score = (npcs_visited * 100) + (dialogues_completed * 25) + time_bonus
  time_bonus = max(0, 300 - time_played_seconds)
"""
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from __init__ import app, db


class HungerHeroScore(db.Model):
    """
    Tracks scores from the Hunger Heroes food bank game.

    Fields:
        id: auto-increment PK
        _user_id: FK to users.id (nullable for anonymous play)
        _player_name: display name (string, max 100)
        _npcs_visited: number of NPCs interacted with (0-5)
        _dialogues_completed: total dialogue lines read
        _score: computed score (int)
        _level_id: which game level (default: 'hunger-heroes-foodbank')
        _time_played_seconds: how long the player spent in-game
        _payload: JSON blob for extensible data
        _timestamp: UTC datetime, auto-set
    """
    __tablename__ = 'hunger_heroes_leaderboard'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=True)
    _player_name = db.Column('player_name', db.String(100), nullable=False)
    _npcs_visited = db.Column('npcs_visited', db.Integer, default=0)
    _dialogues_completed = db.Column('dialogues_completed', db.Integer, default=0)
    _score = db.Column('score', db.Integer, default=0)
    _level_id = db.Column('level_id', db.String(100), default='hunger-heroes-foodbank')
    _time_played_seconds = db.Column('time_played_seconds', db.Integer, default=0)
    _payload = db.Column('payload', db.JSON, nullable=True)
    _timestamp = db.Column('timestamp', db.DateTime, default=datetime.utcnow)

    # Relationship to User model
    user = db.relationship('User', backref='hunger_hero_scores', lazy=True)

    def __init__(self, player_name, npcs_visited=0, dialogues_completed=0,
                 score=None, level_id='hunger-heroes-foodbank',
                 time_played_seconds=0, user_id=None, payload=None):
        self._player_name = player_name
        self._npcs_visited = npcs_visited
        self._dialogues_completed = dialogues_completed
        self._level_id = level_id
        self._time_played_seconds = time_played_seconds
        self._user_id = user_id
        self._payload = payload
        # Server-side score calculation
        self._score = score if score is not None else self.calculate_score()

    @staticmethod
    def calculate_score_from(npcs_visited, dialogues_completed, time_played_seconds):
        """Calculate score from raw values."""
        time_bonus = max(0, 300 - time_played_seconds)
        return (npcs_visited * 100) + (dialogues_completed * 25) + time_bonus

    def calculate_score(self):
        """Calculate score from this instance's fields."""
        return self.calculate_score_from(
            self._npcs_visited,
            self._dialogues_completed,
            self._time_played_seconds
        )

    # --- CRUD ---

    def create(self):
        """Persist this score to the database."""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self):
        """Return dict with camelCase keys for frontend."""
        return {
            'id': self.id,
            'userId': self._user_id,
            'playerName': self._player_name,
            'npcsVisited': self._npcs_visited,
            'dialoguesCompleted': self._dialogues_completed,
            'score': self._score,
            'levelId': self._level_id,
            'timePlayedSeconds': self._time_played_seconds,
            'payload': self._payload or {},
            'timestamp': self._timestamp.isoformat() if self._timestamp else None,
            'user': {
                'id': self.user.id,
                'uid': self.user.uid,
                'name': self.user.name,
            } if self.user else None,
        }

    def update(self, data):
        """Update fields from a dict."""
        if 'playerName' in data:
            self._player_name = data['playerName']
        if 'npcsVisited' in data:
            self._npcs_visited = data['npcsVisited']
        if 'dialoguesCompleted' in data:
            self._dialogues_completed = data['dialoguesCompleted']
        if 'timePlayedSeconds' in data:
            self._time_played_seconds = data['timePlayedSeconds']
        if 'levelId' in data:
            self._level_id = data['levelId']
        if 'payload' in data:
            self._payload = data['payload']
        # Recalculate score server-side
        self._score = self.calculate_score()
        try:
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def delete(self):
        """Remove this row from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    # --- Static Query Helpers ---

    @staticmethod
    def get_by_id(score_id):
        """Look up a score by primary key."""
        return HungerHeroScore.query.get(score_id)

    @staticmethod
    def get_all(level_id=None, limit=50):
        """Return scores ordered by score DESC, optionally filtered by level."""
        query = HungerHeroScore.query
        if level_id:
            query = query.filter_by(_level_id=level_id)
        return query.order_by(HungerHeroScore._score.desc()).limit(limit).all()

    @staticmethod
    def get_user_scores(user_id):
        """Return all scores for a specific user, newest first."""
        return (HungerHeroScore.query
                .filter_by(_user_id=user_id)
                .order_by(HungerHeroScore._score.desc())
                .all())

    @staticmethod
    def get_top_scores(limit=10):
        """Return the top N scores across all users."""
        return (HungerHeroScore.query
                .order_by(HungerHeroScore._score.desc())
                .limit(limit)
                .all())

    # --- Seed Data ---

    @staticmethod
    def init():
        """Seed sample leaderboard data."""
        samples = [
            HungerHeroScore(
                player_name="DemoHero",
                npcs_visited=5,
                dialogues_completed=25,
                level_id="hunger-heroes-foodbank",
                time_played_seconds=150,
            ),
            HungerHeroScore(
                player_name="SpeedRunner",
                npcs_visited=3,
                dialogues_completed=12,
                level_id="hunger-heroes-foodbank",
                time_played_seconds=60,
            ),
            HungerHeroScore(
                player_name="Explorer",
                npcs_visited=5,
                dialogues_completed=30,
                level_id="hunger-heroes-foodbank",
                time_played_seconds=400,
            ),
            HungerHeroScore(
                player_name="Newcomer",
                npcs_visited=1,
                dialogues_completed=4,
                level_id="hunger-heroes-foodbank",
                time_played_seconds=90,
            ),
            HungerHeroScore(
                player_name="FoodBankPro",
                npcs_visited=5,
                dialogues_completed=20,
                level_id="hunger-heroes-foodbank",
                time_played_seconds=200,
            ),
        ]
        for s in samples:
            try:
                db.session.add(s)
                db.session.commit()
                print(f"  Seeded score: {s._player_name} → {s._score}")
            except IntegrityError:
                db.session.rollback()
                print(f"  Skipped duplicate: {s._player_name}")


def initLeaderboard():
    """Top-level init function for main.py generate_data."""
    with app.app_context():
        db.create_all()
        HungerHeroScore.init()
        print("✅ Hunger Heroes leaderboard seeded")
