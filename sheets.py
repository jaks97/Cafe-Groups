import gspread
from oauth2client.service_account import ServiceAccountCredentials

from enum import Enum


class Sheets:
    def __init__(self):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('google_credentials.json', scope)
        gclient = gspread.authorize(creds)

        self.sheet = gclient.open("Discord Puzzles")

        self.puzzles_ws = self.sheet.worksheet("Puzzles")
        self.entries_ws = self.sheet.worksheet("Entries")

    def get_puzzles(self):
        records = self.puzzles_ws.get_all_records()
        puzzles = list(map(lambda record: Puzzle(record['Link'], record['Password']), records))
        return puzzles

    def get_entries(self):
        records = self.entries_ws.get_all_records()
        entries = list(
            map(lambda record:
                Entry(record['User'],
                      Puzzle(record['Puzzle'], record['Password']),
                      EntryStatus[record['Status']]),
                records))
        return entries

    def add_entry(self, entry):
        row = [entry.user, entry.puzzle.link, entry.puzzle.password, entry.status.name]
        self.entries_ws.append_row(row)

    def get_entry_for_user(self, user):
        entries = self.get_entries()
        return next((entry for entry in entries if entry.user == user), None)

    def update_entry_status(self, user, status):
        row = self.entries_ws.find(user).row
        self.entries_ws.update_cell(row, 4, status.name)


class Puzzle:
    def __init__(self, link, password):
        self.link = link
        self.password = password


class Entry:
    def __init__(self, user, puzzle, status):
        self.user = user
        self.puzzle = puzzle
        self.status = status


class EntryStatus(Enum):
    SOLVING = 1,
    SOLVED = 2
