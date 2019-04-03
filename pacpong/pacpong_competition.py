# -*- encoding: utf-8 -*-
"""Pacpong Competition class.

Author: Bas Vonk
Date: 2019-04-01
"""

from datetime import datetime
import pandas as pd
from numpy import sqrt, argmax, absolute, sign, zeros, linalg
from pacpong.google_sheets import GoogleSheets

DECAY_DAYS = 28
NOT_PLAYED_SCORE = 0.5

KEY_HOME_PLAYER = 'home_player'
KEY_AWAY_PLAYER = 'away_player'
KEY_HOME_SCORE = 'home_score'
KEY_AWAY_SCORE = 'away_score'
KEY_SCORE = 'score'
KEY_DATE = 'date'


class PacpongCompetition:

    def __init__(self, google_sheets_obj: GoogleSheets):

        self.google_sheets_obj = google_sheets_obj
        self.match_records = None
        self.players = None
        self.head_to_head_points = {}
        self.head_to_head_scores = {}
        self.matrix_a = None
        self.df_ranking = pd.DataFrame()
        self.leading_eigenvector = None
        self.today = datetime.now().date()

    def _add_match_records(self):
        """Add the match records to the competition."""
        self.match_records = self.google_sheets_obj.sheet_matches.get_all_records()

    def _add_players(self):
        """Add the players to the competition."""
        if self.match_records is None:
            self._add_match_records()

        home_players = [match.get(KEY_HOME_PLAYER) for match in self.match_records]
        away_players = [match.get(KEY_AWAY_PLAYER) for match in self.match_records]

        self.players = list(set(home_players + away_players))

    def _add_head_to_head_scores_entry(self, player_1, player_2, score):
        """Add a specific entry to the head_to_head_scores attribute."""
        if self.head_to_head_points.get(player_1) is None:
            self.head_to_head_points.update({player_1: {player_2: score}})

        elif self.head_to_head_points[player_1].get(player_2) is None:
            self.head_to_head_points[player_1].update({player_2: score})

        else:
            self.head_to_head_points[player_1][player_2] += score

    def _get_decay_factor(self, date):
        """Get the decay factor."""
        factor = 1 - (self.today - datetime.strptime(date, '%Y-%m-%d').date()).days / DECAY_DAYS
        return max(factor, 0)

    def _add_head_to_head_points(self):
        """Add head to head points to the head_to_head_points attribute."""
        for match in self.match_records:

            score = self._get_decay_factor(match[KEY_DATE]) * match[KEY_HOME_SCORE]
            self._add_head_to_head_scores_entry(match[KEY_HOME_PLAYER],
                                                match[KEY_AWAY_PLAYER],
                                                score)

            score = self._get_decay_factor(match[KEY_DATE]) * match[KEY_AWAY_SCORE]
            self._add_head_to_head_scores_entry(match[KEY_AWAY_PLAYER],
                                                match[KEY_HOME_PLAYER],
                                                score)

    def _add_head_to_head_scores(self):
        """Add head to head scores to the head_to_head_scores attribute."""
        if not self.head_to_head_points:
            self._add_head_to_head_points()

        for player_1, opponents in self.head_to_head_points.items():
            self.head_to_head_scores[player_1] = {}
            for player_2, points in opponents.items():
                s_i_j = points
                s_j_i = self.head_to_head_points[player_2][player_1]
                self.head_to_head_scores[player_1].update({player_2: self.a_i_j(s_i_j, s_j_i)})

    def _add_matrix_a(self):
        """Add the matrix A to the competition."""
        if not self.head_to_head_scores:
            self._add_head_to_head_scores()

        self.matrix_a = zeros([len(self.players), len(self.players)])

        for idx1, player_1 in enumerate(self.players):
            for idx2, player_2 in enumerate(self.players):
                try:
                    a_i_j = self.head_to_head_scores[player_1][player_2]
                except KeyError:
                    a_i_j = NOT_PLAYED_SCORE

                self.matrix_a[idx1, idx2] = a_i_j
                self.df_ranking.at[player_1, player_2] = a_i_j

    def _add_leading_eigenvector(self):
        """Add the leading eigenvector."""
        if self.matrix_a is None:
            self._add_matrix_a()

        eigenvalues, eigenvectors = linalg.eig(self.matrix_a)

        # Retrieve the index of the largest eigenvalue, as stated in the paper
        index: int = argmax(eigenvalues)

        # Get the absolute eigenvector
        self.leading_eigenvector = absolute(eigenvectors[:, index])

    def _add_leading_eigenvector_to_df_ranking(self):
        """Add the leading eigenvector the the df_ranking attribute."""
        if self.leading_eigenvector is None:
            self._add_leading_eigenvector()

        self.df_ranking.at[0:len(self.players), KEY_SCORE] = self.leading_eigenvector
        self.df_ranking.at[KEY_SCORE, 0:len(self.players)] = self.leading_eigenvector

    def _sort_df_ranking(self):
        """Sort the df_ranking according to the score."""
        if KEY_SCORE not in self.df_ranking.columns:
            self._add_leading_eigenvector_to_df_ranking()

        self.df_ranking.sort_values(by=KEY_SCORE, axis=0, ascending=False, inplace=True)
        self.df_ranking.sort_values(by=KEY_SCORE, axis=1, ascending=False, inplace=True)

    def _get_df_ranking(self):
        """Get df_ranking for the competition."""
        self._add_match_records()
        self._add_players()
        self._add_head_to_head_points()
        self._add_head_to_head_scores()
        self._add_matrix_a()
        self._add_leading_eigenvector()
        self._add_leading_eigenvector_to_df_ranking()
        self._sort_df_ranking()

        return self.df_ranking

    def update(self):
        """Update the pacpong competition ranking."""
        df_ranking = self._get_df_ranking()
        self.google_sheets_obj.update_results_sheet(df_ranking)

    def a_i_j(self, s_i_j: int, s_j_i: int) -> float:
        """Calculate the value a_i_j."""
        return self.h((s_i_j + 1) / (s_i_j + s_j_i + 2))

    @staticmethod
    def h(x: float) -> float:
        """Calculate the value for h."""
        return 0.5 + 0.5 * sign(x - 0.5) * sqrt(abs(2 * x - 1))
