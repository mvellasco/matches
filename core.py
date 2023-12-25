import csv
from collections import deque
from collections.abc import MutableSequence
from datetime import datetime

import pandas


class Team:
    """A pythonic football team."""

    def __init__(self, *, city, team, team_id, type, geo, grouping):
        self.city = city
        self.team_name = team
        self.team_id = team_id
        self.type = type  # this will be national most of the times
        self.geo = geo
        self.group = grouping

    def __repr__(self):
        return f"<Team {self.team_name} - Group {self.group}>"

    def __gt__(self, other):
        return (self.group, self.team_name) > (other.group, other.team_name)

    def __lt__(self, other):
        return (self.group, self.team_name) < (other.group, other.team_name)


class TeamCollection(MutableSequence):
    """A pythonic collection of Teams."""

    __slots__ = ("_teams",)  # this isn't necessary, it just demonstrates usage of slots in objects.

    def __init__(self, teams = None):
        self._teams = deque(sorted(teams, key=lambda obj: obj.group), maxlen=32) if teams else deque([], maxlen=32)
        self.sort()

    def __contains__(self, elem):
        return elem in self._teams

    def __iter__(self):
        return (elem for elem in self._teams)

    def __len__(self):
        return len(self._teams)

    def __setitem__(self, pos, elem):
        self._teams[pos] = elem

    def __getitem__(self, index_or_id):
        team = None
        try:
            team = self._teams[index_or_id]
        except IndexError as exc:
            for _team in self._teams:
                if _team.team_id == str(index_or_id):
                    team = _team
                    break
            if team is None:
                raise exc
        
        return team

    def __delitem__(self, pos):
        self._teams.pop(pos)

    def __repr__(self):
        return repr(self._teams)

    def __call__(self, group):
        return [team for team in self if team.group == group]

    def append(self, elem):
        self._teams.append(elem)

    def insert(self, pos, elem):
        if pos == len(self):
            self._teams.append(elem)
        else:
            self._teams[pos] = elem

    def sort(self, reverse = False):
        self._teams = sorted(self, reverse=reverse)


class Match:
    """A football match."""

    def __init__(self, *args, **kwargs):
        self.match_id = kwargs.get("match_id")
        self.label = kwargs.get("label")
        self.group = kwargs.get("group")
        self.date = datetime.fromisoformat(kwargs.get("date"))
        self.home_team = kwargs.get("home")  # team_collection[int(kwargs.get("home"))]
        self.away_team = kwargs.get("away")  # team_collection[int(kwargs.get("away"))]
        self.winner = kwargs.get("winner")  # team_collection[int(kwargs.get("winner"))]
        self.home_score = kwargs.get("home_score")
        self.away_score = kwargs.get("away_score")

    def __repr__(self):
        return f"<Match: {self.label}>"


########################################### Tests ###########################################
def test_team_collection():
    team_collection = TeamCollection()

    with open("data/teams.csv", "r", newline="") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            team_collection.append(Team(**row))

        # sorted(team_collection) will also work
    
    assert all(isinstance(team, Team) for team in team_collection)


def test_match_collection():
    with open("data/matches.csv", "r", newline="") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        matches = []
        raw_matches = list(csv_reader)
        for raw_match in raw_matches:
            matches.append(Match(**raw_match))

    match_collection = list(sorted(matches, key=lambda obj: obj.date))

    assert all(isinstance(match, Match) for match in match_collection)


def test_team_matches_pandas():
    team_matches = pandas.read_csv("data/team_match.csv")

    team_matches["team_pass_accuracy"] = team_matches["pass_accurate"] * 100 / team_matches["pass"]
    team_matches["opp_pass_accuracy"] = team_matches["pass_accurate_opp"] * 100 / team_matches["pass_opp"]
    team_matches["match_display"] = team_matches["team"] + " x " + team_matches["opp"]

    matches_df = team_matches[
        [
            "match_display",
            "pass",
            "pass_accurate",
            "team_pass_accuracy",
            "pass_opp",
            "pass_accurate_opp",
            "opp_pass_accuracy",
        ]
    ]
    matches_df = matches_df[(matches_df["pass"] >= 600) & (matches_df["pass_opp"] >= 300)]
    matches_df.sort_values("team_pass_accuracy", ascending=False)

    assert isinstance(matches_df, pandas.DataFrame)
    assert len(matches_df) == 5
    assert matches_df.iloc[0]["team_pass_accuracy"] > matches_df.iloc[1]["team_pass_accuracy"]
