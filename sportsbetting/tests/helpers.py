from django.utils import timezone

from sportsbetting.models import BettingLine, Game, GoverningBody, Sport, Team


def create_common_test_data():
    sport = Sport.objects.create(name="Test Sport")
    gov_body = GoverningBody.objects.create(sport=sport, name="Test GB", type="pro")
    team1 = Team.objects.create(
        name="Team 1", downloaded=False, governing_body=gov_body
    )
    team2 = Team.objects.create(
        name="Team 2", downloaded=False, governing_body=gov_body
    )
    game = Game.objects.create(
        sport=sport,
        governing_body=gov_body,
        home_team=team1,
        away_team=team2,
        start_datetime=timezone.now(),
    )
    betting_line = BettingLine.objects.create(
        game=game,
        spread=-3.5,  # Replaced home_spread with spread
        over=45.5,  # Replaced over_under with over
    )
    return {
        "sport": sport,
        "gov_body": gov_body,
        "team1": team1,
        "team2": team2,
        "game": game,
        "betting_line": betting_line,
    }
