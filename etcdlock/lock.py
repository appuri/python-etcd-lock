import etcd
import uuid
from threading import Timer

class Lock(object):

    """
    Lock object using etcd keys to atomically compare and swap.
    """

    def __init__(self, client, key, ttl=60, renewSecondsPrior=5, timeout=None):
        """
        Initialize a lock object.
        Args:
            client (Client):  etcd client to use for communication.
            key (string):  key to lock.
            ttl (int):  ttl (in seconds) for the lock to live. Defaults to 60 seconds.
            renewSecondsPrior (int or None): time before the end of the ttl period to renew the lock.
                Defaults to 5 seconds. Specify None to disable lock renewal.
            timeout (int or None): default timeout to use for aquisition (see acquire).
        """
        if not isinstance(client, etcd.Client):
            raise ValueError("A python-etcd Client must be provided")
        if key is None or key is '':
            raise ValueError("A etcd key must be specified")
        if ttl is None or ttl <= 0:
            raise ValueError("A positive TTL must be specified")
        if renewSecondsPrior is not None:
            if not isinstance(renewSecondsPrior, int) or renewSecondsPrior < 0:
                raise ValueError("A positive prior renew must be specified, or None to not renew")
            if ttl - renewSecondsPrior < 1:
                raise ValueError("The renew prior time is too close to initial aquisition time - hold the lock for at least 2 seconds")

        self.client = client
        if not key.startswith('/'):
            key = '/' + key
        self.key = key
        self.ttl = ttl
        self.renewSecondsPrior = renewSecondsPrior
        self._index = None
        self.token = None
        self.timeout = timeout

    def __enter__(self):
        return self.acquire()

    def __exit__(self, type, value, traceback):
        return self.release()

    def acquire(self, **kwargs):
        """
        Aquire the lock. Returns True if the lock was acquired; False otherwise.

        timeout (int): Timeout to wait for the lock to change if it is already acquired.
            Defaults to what was provided during initialization, which will block and retry until acquired. 
        """
        token = str(uuid.uuid4())
        attempted = False
        while self.token is None:
            try:
                self.client.test_and_set(self.key, token, "0", ttl=self.ttl)
                self.token = token
            except etcd.EtcdKeyNotFound, e:
                try:
                    self.client.write(self.key, token, prevExist=False, recursive=True, ttl=self.ttl)
                    self.token = token
                except etcd.EtcdAlreadyExist, e:
                    pass # someone created the right before us
            except ValueError, e:
                # someone else has the lock
                if 'timeout' in kwargs or self.timeout is not None:
                    if attempted is True: return False
                    kwargs.setdefault("timeout", self.timeout)
                    try:
                        self.client.read(self.key, wait=True, timeout=kwargs["timeout"])
                        attempted = True
                    except etcd.EtcdException, e:
                        return False
                else:
                    self.client.watch(self.key)

        if self.renewSecondsPrior is not None:
            def renew():
                if (self.renew()):
                    Timer(self.ttl, self.renew)
            Timer(self.ttl - self.renewSecondsPrior, lambda: self.renew())
        else:
            def cleanup():
                if self.token is token:
                    self.token = None
            Timer(self.ttl, cleanup)

        return True

    def renew(self):
        """
        Renew the lock if acquired.
        """
        if (self.token is not None):
            try:
                self.client.test_and_set(self.key, self.token, self.token, ttl=self.ttl)
                return True
            except ValueError, e:
                self.token = None
                return False

    def is_locked(self):
        """
        Return True if the lock has been and is currently acquired; False otherwise.
        """
        return self.token is not None

    def release(self):
        """
        Release the lock if acquired.
        """
        # TODO: thread safety (currently the lock may be acquired for one more TTL length)
        if (self.token is not None):
            try:
                self.client.test_and_set(self.key, 0, self.token)
            except (ValueError, etcd.EtcdKeyError, etcd.EtcdKeyNotFound) as e:
                pass # the key already expired or got acquired by someone else
            finally:
                self.token = None