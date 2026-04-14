"""
Hunger Heroes Game Leaderboard API

Endpoints:
  GET  /api/hunger-heroes/leaderboard           → all scores (?levelId=&limit=)
  GET  /api/hunger-heroes/leaderboard/top/<n>    → top N scores
  POST /api/hunger-heroes/leaderboard            → submit a new score (auth required)
  GET  /api/hunger-heroes/leaderboard/user/<id>  → scores for specific user
"""
from flask import Blueprint, g, request
from flask_restful import Api, Resource
from api.jwt_authorize import token_required
from model.game_leaderboard import HungerHeroScore


hunger_heroes_api = Blueprint('hunger_heroes_api', __name__, url_prefix='/api/hunger-heroes')
hunger_heroes_restful = Api(hunger_heroes_api)


class LeaderboardAPI(Resource):
    """GET all scores / POST a new score."""

    def get(self):
        """
        Return leaderboard scores.

        Query params:
            levelId (str): Filter by game level (optional)
            limit (int): Max results, default 50
        """
        level_id = request.args.get('levelId')
        limit = request.args.get('limit', 50, type=int)
        scores = HungerHeroScore.get_all(level_id=level_id, limit=limit)
        return [s.read() for s in scores]

    @token_required()
    def post(self):
        """
        Submit a new score. Requires authentication.

        Expects JSON body:
            {
                "playerName": "HeroPlayer",
                "npcsVisited": 5,
                "dialoguesCompleted": 23,
                "timePlayedSeconds": 180,
                "levelId": "hunger-heroes-foodbank",
                "payload": { ... }
            }

        Score is calculated server-side — client score is ignored.
        """
        body = request.get_json(silent=True)
        if not body:
            return {"message": "Missing JSON body"}, 400

        # Validate required fields
        player_name = body.get('playerName')
        npcs_visited = body.get('npcsVisited')
        dialogues_completed = body.get('dialoguesCompleted')
        time_played_seconds = body.get('timePlayedSeconds')

        if not player_name:
            return {"message": "playerName is required"}, 400
        if npcs_visited is None:
            return {"message": "npcsVisited is required"}, 400
        if dialogues_completed is None:
            return {"message": "dialoguesCompleted is required"}, 400
        if time_played_seconds is None:
            return {"message": "timePlayedSeconds is required"}, 400

        # Validate types / ranges
        try:
            npcs_visited = int(npcs_visited)
            dialogues_completed = int(dialogues_completed)
            time_played_seconds = int(time_played_seconds)
        except (ValueError, TypeError):
            return {"message": "npcsVisited, dialoguesCompleted, and timePlayedSeconds must be integers"}, 400

        if npcs_visited < 0 or npcs_visited > 50:
            return {"message": "npcsVisited must be between 0 and 50"}, 400

        # Extract authenticated user
        current_user = g.current_user
        user_id = current_user.id if current_user else None

        # Server-side score calculation
        score = HungerHeroScore.calculate_score_from(
            npcs_visited, dialogues_completed, time_played_seconds
        )

        entry = HungerHeroScore(
            player_name=player_name,
            npcs_visited=npcs_visited,
            dialogues_completed=dialogues_completed,
            score=score,
            level_id=body.get('levelId', 'hunger-heroes-foodbank'),
            time_played_seconds=time_played_seconds,
            user_id=user_id,
            payload=body.get('payload'),
        )

        created = entry.create()
        if created:
            return created.read(), 201
        return {"message": "Failed to save score"}, 500


class LeaderboardTopAPI(Resource):
    """GET top N scores."""

    def get(self, n):
        """Return top N scores across all users."""
        try:
            n = int(n)
        except (ValueError, TypeError):
            return {"message": "n must be an integer"}, 400
        if n < 1 or n > 200:
            return {"message": "n must be between 1 and 200"}, 400
        scores = HungerHeroScore.get_top_scores(limit=n)
        return [s.read() for s in scores]


class LeaderboardUserAPI(Resource):
    """GET all scores for a specific user."""

    def get(self, user_id):
        """Return all scores for user_id, ordered by score DESC."""
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return {"message": "user_id must be an integer"}, 400
        scores = HungerHeroScore.get_user_scores(user_id)
        return [s.read() for s in scores]


# --- Register resources ---
hunger_heroes_restful.add_resource(LeaderboardAPI, '/leaderboard')
hunger_heroes_restful.add_resource(LeaderboardTopAPI, '/leaderboard/top/<int:n>')
hunger_heroes_restful.add_resource(LeaderboardUserAPI, '/leaderboard/user/<int:user_id>')
