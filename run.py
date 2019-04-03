from pacpong.google_sheets import GoogleSheets
from pacpong.pacpong_competition import PacpongCompetition
from pprint import pprint


if __name__ == '__main__':

    google_sheets_obj = GoogleSheets(json_keyfile_name='credentials.json',
                                     sheet_key='1QVdLOnTS6fdbcIlSdhEmQ5nU9SwphgFOo_otDeTOob0')

    pacpong_competition_obj = PacpongCompetition(google_sheets_obj=google_sheets_obj)
    pacpong_competition_obj.update()
