import sys

from sqlalchemy import select, create_engine
from sqlalchemy.orm.session import sessionmaker
from notebook import Notebook, Base


class Menu:
    """Display a menu and respond to choices when run."""

    def __init__(self):
        # can make one session for full run of the menu, 
        # or potentially create a new session for each action
        self._session = Session()

        # get notebook from db (several options)
        # self._notebook = self._session.query(Notebook).first() # older style deprecated in 2.0
        # self._notebook = self._session.scalars(select(Notebook)).first()
        self._notebook = self._session.get(Notebook, 1)

        # if there is no notebook, let's make one and add it to the DB
        if self._notebook is None:
            self._notebook = Notebook()
            self._session.add(self._notebook)
            self._session.commit()
            
        self._choices = {
            "1": self._show_notes,
            "2": self._search_notes,
            "3": self._add_note,
            "4": self._modify_note,
            "5": self._quit,
        }

    def _display_menu(self):
        print(
"""
Notebook Menu

1. Show all Notes
2. Search Notes
3. Add Note
4. Modify Note
5. Quit
""")

    def run(self):
        """Display the menu and respond to choices."""
        while True:
            self._display_menu()
            choice = input("Enter an option: ")
            action = self._choices.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))

    def _show_notes(self, notes=None):
        if notes is None:
            notes = self._notebook.all_notes()
        for note in notes:
            print(str(note))

    def _search_notes(self):
        filter_string = input("Search for: ")
        notes = self._notebook.search(filter_string)
        self._show_notes(notes)

    def _add_note(self):
        memo = input("Enter a memo: ")
        self._notebook.new_note(memo, self._session)
        print("Your note has been added.")
        self._session.commit()

    def _modify_note(self):
        id = input("Enter a note id: ")
        memo = input("Enter a memo: ")
        tags = input("Enter tags: ")
        if memo:
            self._notebook.modify_memo(id, memo)
        if tags:
            self._notebook.modify_tags(id, tags)
        self._session.commit()


    def _quit(self):
        sys.exit(0)


if __name__ == "__main__":
    # connect to the database
    # in general a connection string looks like...
    # dialect+driver://username:password@host:port/database
    engine = create_engine("sqlite:///notebook.db", echo=True) 
    # echo can be used to see the actual queries that are run

    # creates SQL tables based on the OOP models
    # if the tables already exist, this does nothing (even if there was a change)
    Base.metadata.create_all(engine)

    # session factory
    Session = sessionmaker(engine) 
    
    Menu().run()