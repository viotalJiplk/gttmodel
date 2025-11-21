import datetime
from ..utils import dbConn, Db, Cursor
from ..utils import defaultLogger
from ..utils import genState
from ..utils import config


class StateModel:
    """Representation of state in discord login

    Attributes:
            state (str): random string representing unique state
            date (datetime.datetime): time of state expiration
    """
    def __init__(self, state: str, date:datetime.datetime):
        """Initializes representation of state in discord login

        Args:
            state (str): random string representing unique state
            date (datetime.datetime): time of state expiration
        """
        self.state = state
        self.date = date

    @classmethod
    @dbConn()
    def create(cls, cursor: Cursor, db: Db):
        """Creates new state

        Returns:
            StateModel: new state
        """
        state = genState(200)
        date = datetime.datetime.now() + datetime.timedelta(0, config.discord.state_ttl)
        query = "INSERT INTO `states` (`state`, `date`) VALUES (%(state)s, %(date)s);"
        cursor.execute(query, {'state': state,'date': date})
        return cls(state=state, date=date)

    @classmethod
    @dbConn()
    def testAndDelete(cls, state: str, cursor: Cursor, db: Db):
        """Tests and deletes if state exists

        Args:
            state (str): state to test

        Returns:
            bool: does state exist
        """
        query = "DELETE FROM states WHERE `state` = %(state)s;"
        cursor.execute(query, {'state': state})

        if cursor.rowcount == 1:
            return True
        elif cursor.rowcount > 1:
            defaultLogger.warning("DB: The state was not unique.")

        return False
