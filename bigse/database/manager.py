import contextlib
import datetime
import json
import logging
import os
import typing
from importlib import resources

import psycopg2

from bigse.database import sql

_LOGGER = logging.getLogger("bigse.database")

class DatabaseInteractionManager:
    """
    Class that manages all database interactions.
    """

    def __init__(self) -> None:
        _LOGGER.debug("Created DatabaseInteractionManager instance: %r", self)
        self._connector = None

    @property
    def connector(self):
        if self._connector is None:
            self._connector = self._create_database_connection()
        return self._connector

    def close_connection(self):
        if self._connector is None:
            return
        self._connector.close()
        _LOGGER.debug("Connection closed: %r", self)

    @staticmethod
    def _create_database_connection():
        _LOGGER.debug("Connecting to database")
        database_url = os.environ["DATABASE_URL"]
        return psycopg2.connect(database_url)

    @contextlib.contextmanager
    def get_cursor(self, commit: bool = False):
        """
        Context manager to automatically manage database connections. Acquires a connection for
        use within the context manager and gives a cursor to execute queries through. Closes the cursor
        and puts the connection back into the pool once the context manager has been exited.

        Args:
            commit (:obj:`bool`): Whether to commit changes to the database once the context is exited.
                Defaults to ``False``.
        """
        _conn = self.connector
        cursor = _conn.cursor()
        try:
            yield cursor
        finally:
            if commit:
                _conn.commit()

    def create_schema(self) -> None:
        _LOGGER.info("Creating database schema")
        schema = resources.read_text(sql, "schema.sql")
        with self.get_cursor(commit=True) as cur:
            cur.execute(schema)

    def get_ids(self) -> typing.Optional[typing.List[int]]:
        with self.get_cursor() as cur:
            cur.execute("SELECT docid FROM documents;")
            ids = cur.fetchall()
            print(ids)
        return ids if ids else None
    
    def get_embeddings(self) -> typing.Optional[typing.List[str]]:
        with self.get_cursor() as cur:
            cur.execute("SELECT docembedding FROM documents;")
            embeddings = cur.fetchall()
            print(embeddings)
        return embeddings if embeddings else None
    
    def get_ids_embeddings(self) -> typing.Optional[typing.List[str]]:
        with self.get_cursor() as cur:
            cur.execute("SELECT docid, docembedding FROM documents;")
            list = cur.fetchall()
            print(list)
            ids = [x[0] for x in list]
            embeddings = [json.loads(x[1]) for x in list]
        return (ids, embeddings) if embeddings else ([],[])
    
    def get_ids_embeddings_not_added(self) -> typing.Optional[typing.List[str]]:
        with self.get_cursor() as cur:
            cur.execute("SELECT docid, docembedding FROM documents WHERE added = false;")
            list = cur.fetchall()
            
            ids = [x[0] for x in list]
            print(ids)
            embeddings = [json.loads(x[1]) for x in list]
        return (ids, embeddings) if embeddings else ([],[])
    
    def create_doc_entry(
        self,
        docname: str,
        docpath: str,
        doclink: str,
        docembedding: str
    ) -> None:
        with self.get_cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO documents(docname, docpath, doclink, docembedding) VALUES(%s, %s, %s, %s);",
                (docname, docpath, doclink, docembedding),
            )

    def get_doc_entry(
        self,
        docid: int
    ) -> None:
        with self.get_cursor() as cur:
            cur.execute(
                "SELECT docname, docpath, doclink, docembedding FROM documents where docid = %s;",
                (int(docid),),
            )
            doc = cur.fetchone()
            print(doc)
        return doc if doc else None
    
    def get_doc_entry_from_path(
        self,
        docpath: str
    ) -> None:
        with self.get_cursor() as cur:
            cur.execute(
                "SELECT docname, docpath, doclink, docembedding FROM documents where doclink = %s;",
                (docpath,),
            )
            doc = cur.fetchone()
        return doc if doc else None
    
    def set_doc_as_added(
        self,
        docid: int,
    ) -> None:
        with self.get_cursor(commit=True) as cur:
            cur.execute(
                "UPDATE documents SET added=true WHERE docid = %s;",
                (int(docid),),
            )
    
    def empty(
        self
    ) -> None:
        with self.get_cursor(commit=True) as cur:
            cur.execute(
                "DELETE FROM documents;"
            )
