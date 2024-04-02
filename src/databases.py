import os

from loguru import logger
from neo4j import GraphDatabase


class Neo4J:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4J, cls).__new__(cls)
            cls._instance._initialize()
            logger.info("Neo4J instance created")
        return cls._instance
    
    def _initialize(self):
        uri = os.getenv("NEO4J_URI")
        username, password = os.getenv("NEO4J_AUTH").split("/")
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()
