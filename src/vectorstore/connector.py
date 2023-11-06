import threading
import time
from typing import Union

import chromadb


class ChromaClientMonitor(threading.Thread):
    def __init__(self, host, port, check_interval=60):
        super(ChromaClientMonitor, self).__init__()
        self.host = host
        self.port = port
        self.check_interval = check_interval

        self._logger = None
        self._client = None
        self._create_http_client()

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        self._client = client

    def _create_http_client(self):
        if self.client is None:
            self.client = chromadb.HttpClient(host=self.host, port=self.port)

    def check_health(self):
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False

    def run(self, *args, **kwargs):
        while True:
            if self.logger is None:
                continue

            if not self.check_health():
                self.logger.critical("Chroma service is down.")
            else:
                self.logger.info("Chroma service is healthy.")

            time.sleep(self.check_interval)


class ChromaCRUD:
    def __init__(
        self, client: Union[chromadb.Client, chromadb.PersistentClient]
    ):
        """
        Chroma CRUD object with methods to Create, Read, Update, Delete
        for Chroma collections.
        **Parameters**
        * `client`: A Chroma client.
        """
        self.client = client

    def get_collections(self):
        return self.client.list_collections()

    def create_collection(self, collection_name: str):
        return self.client.create_collection(collection_name)

    def delete_collection(self, collection_name: str):
        self.client.delete_collection(collection_name)

    def check_health(self):
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False

    def create_item(
        self, collection_name: str, embeddings, metadatas, documents, ids
    ):
        collection = self.client.get_or_create_collection(collection_name)
        collection.add(
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
            ids=ids,
        )
        return collection

    def read_item(self, collection_name: str, ids):
        collection = self.client.get_collection(collection_name)
        if collection:
            return collection.get(ids=ids)
        else:
            return None

    def update_item(
        self,
        collection_name: str,
        ids,
        embeddings=None,
        metadatas=None,
        documents=None,
    ):
        collection = self.client.get_collection(collection_name)
        if collection:
            collection.update(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
            )
        else:
            raise Exception("Collection does not exist")

        return collection

    def delete_item(self, collection_name: str, ids):
        collection = self.client.get_collection(collection_name)
        if collection:
            collection.delete(ids=ids)
        else:
            raise Exception("Collection does not exist")

        return collection


monitor = ChromaClientMonitor(host="localhost", port=8000)
client = monitor.client
