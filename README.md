## Python Lock library for ETCD 2.0

Since ETCD 0.4, all [the built in modules were removed](https://groups.google.com/d/msg/etcd-dev/ubcPWuL8wSg/7GeaxSHhIb0J), including the locking module. The API still provides an atomic compare-and-swap method to implement locking, thus providing the core functionality to create semaphores and mutexes. This library is built on top of that, matching the API that was in [python-etcd](https://github.com/jplana/python-etcd) before it was removed as much as possible.

[![Circle CI](https://circleci.com/gh/appuri/python-etcd-lock.svg?style=shield)](https://circleci.com/gh/appuri/python-etcd-lock)

#### Simple Usage

```python
import etcd
from etcdlock import Lock

lock = Lock(etcd.Client(), 'path/to/my/key')
while lock
    # lock is acquired
    # lock will renew itself by default until released
    # do work
    request = ....

    # check if we still have the lock
    if lock.is_locked() is False:
        return
```

#### Explicit Usage

```python
import etcd
from etcdlock import Lock

client = client = etcd.Client(host='api.example.com', protocol='https', port=443, version_prefix='/etcd')
lock = Lock(client, 'path/to/my/key', ttl=30, renewSecondsPrior=)
if lock.acquire(timeout=20):
    t = Thread(target=someheavywork)
    t.run()
    t.wait()
    lock.renew()
    # some other work
    lock.release() # not recommended, use a context manager
else
    # failed to acquire the lock in 20 seconds
    pass
```

Please see [the tests](https://github.com/appuri/python-etcd-lock/blob/master/tests/lock_tests.py) while the documentation is lacking, thanks.
