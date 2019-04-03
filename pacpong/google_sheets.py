# -*- encoding: utf-8 -*-
"""Google Sheets class.

Author: Bas Vonk
Date: 2019-04-01
"""

from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials as sac
from pytz import timezone
import gspread

SHEET_MATCHES_NAME = 'matches'
SHEET_RESULTS_NAME = 'results'

SCOPE = ['https://spreadsheets.google.com/feeds']


class GoogleSheets:

    def __init__(self, json_keyfile_name, sheet_key):

        credentials = sac.from_json_keyfile_name(json_keyfile_name, SCOPE)
        spreadsheet = gspread.authorize(credentials).open_by_key(sheet_key)

        self.sheet_matches = spreadsheet.worksheet(SHEET_MATCHES_NAME)
        self.sheet_results = spreadsheet.worksheet(SHEET_RESULTS_NAME)

    @staticmethod
    def get_current_datetime():
        return datetime.now(timezone('Europe/Amsterdam')).strftime('%Y-%m-%d %H:%M')

    def update_results_sheet(self, df_ranking):

        playercount = len(df_ranking.index) - 1

        # Get the range for the results sheet
        ranking_range = self.sheet_results.range(1, 1, playercount + 1, playercount + 2)

        for cell in ranking_range:

            # Put updated-time in A1
            if cell.row == 1 and cell.col == 1:
                cell.value = self.get_current_datetime()
                continue

            # Put column headers
            if cell.row == 1 and cell.col > 1 and cell.col < playercount + 2:
                cell.value = df_ranking.columns[cell.col - 2]
                continue

            # Put row headers
            if cell.col == 1 and cell.row > 1:
                cell.value = f"{cell.row - 1}. {df_ranking.index[cell.row - 2]}"
                continue

            # Put 'diagonal' word
            if cell.col > 1 and cell.row > 1 and cell.row == cell.col:
                cell.value = 'diagonal'
                continue

            # Put scores in the cells
            if cell.row > 1 and cell.col > 1 and cell.col < playercount + 2:
                cell.value = round(df_ranking.iloc[cell.row - 2, cell.col - 2] * 100)
                continue

            # This is the header for the points colummn
            if cell.col == playercount + 2 and cell.row == 1:
                cell.value = 'Points'
                continue

            # This is the column with the points
            if cell.col is playercount + 2 and cell.row > 1:
                cell.value = f"{int(df_ranking.iloc[cell.row - 2, cell.col - 2] * 100)} ({cell.row - 1})"  # noqa
                continue

        self.sheet_results.update_cells(ranking_range)
