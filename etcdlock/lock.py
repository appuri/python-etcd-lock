import etcd

class Lock(object):

    """
    Lock object using etcd keys to atomically compare and swap.
    """

    def __init__(self, client, key, ttl=60):
        """
        Initialize a lock object.
        Args:
            client (Client):  etcd client to use for communication.
            key (string):  key to lock.
            ttl (int):  ttl (in seconds) for the lock to live. Defaults to 60 seconds.
            refresh (int): time before the end of the ttl period to refresh the lock. Defaults to 5 seconds.
        """
        if ttl is None or ttl is 0:
            raise ValueError("A positive TTL must be specified")
        if key is None or key is '':
            raise ValueError("A etcd key must be specified")
        if not isinstance(client, etcd.Client):
            raise ValueError("A python-etcd Client must be provided")

        self.client = client
        if not key.startswith('/'):
            key = '/' + key
        self.key = key
        self.ttl = ttl
        self._index = None

    def __enter__(self):
        self.acquire()

    def __exit__(self, type, value, traceback):
        self.release()

    def acquire(self): pass

    def release(self): pass
