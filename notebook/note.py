from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column

from notebook import Base


class Note(Base):
    """Represent a note in the notebook. Match against a
    string in searches and store tags for each note."""

    __tablename__ = "note"

    _id = mapped_column(Integer, primary_key=True)
    _notebook_id = mapped_column(Integer, ForeignKey("notebook._id"))
    _memo = mapped_column(String)
    _tags = mapped_column(String)
    _creation_date = mapped_column(DateTime)

    # last_id = 0

    def __init__(self, memo, tags=""):
        """initialize a note with memo and optional
        space-separated tags. Automatically set the note's
        creation date and a unique id."""

        self._memo = memo
        self._tags = tags
        self._creation_date = datetime.today()

        # Note.last_id += 1
        # self._id = Note.last_id

    def match(self, filter):
        """Determine if this note matches the filter
        text. Return True if it matches, False otherwise.

        Search is case sensitive and matches both text and
        tags."""

        return filter in self._memo or filter in self._tags

    def id_matches(self, id):
        """
        Determine if this note has the given id
        """
        return self._id == int(id)

    def update_memo(self, memo):
        self._memo = memo

    def update_tags(self, tags):
        self._tags = tags

    def __str__(self):
        # this print doesn't belong here. it's just to demonstrate the backref
        print(f"This note has a backref to: {self._notebook}")
        return f"{self._id}: {self._memo}\n{self._tags}"

    def __lt__(self, other):
        return self._id < other._id

    def __eq__(self, other):
        return self._id == other._id