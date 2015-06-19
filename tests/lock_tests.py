from robber import expect
import unittest
import etcd
import expectlambda

import os
import sys
sys.path.insert(0, os.path.abspath("."))
from etcdlock import Lock

import random
import time
from threading import Thread

class EtcdLockTests(unittest.TestCase):
    def setUp(self):
        self.client = etcd.Client()
        self.lock = Lock(self.client, "lock-%d" % random.uniform(1,100000))

    def teardown(self):
        if (self.lock != None and self.lock.token != None):
            self.lock.release()

    def test_it_should_require_an_etcd_client(self):
        expect(lambda: Lock(None, 'lock/foo')).to.raise_error(ValueError)

    def test_it_should_require_a_valid_ttl(self):
        expect(lambda: Lock(self.client, 'lock/foo', ttl=0)).to.raise_error(ValueError)

    def test_it_should_require_an_etcd_key(self):
        expect(lambda: Lock(self.client, key=None)).to.raise_error(ValueError)

    def test_it_should_be_able_to_be_acquired_and_released(self):
        self.lock.acquire()
        node = self.client.get(self.lock.key)
        print node
        expect(node.value).to.eq(self.lock.token)
        expect(node.ttl).to.eq(60)
        self.lock.release()
        expect(self.client.get(self.lock.key).value).to.eq("0")

    def test_it_should_not_aquire_a_lock_already_acquired(self):
        self.lock.acquire()
        def acquire_again():
            print "in the other thread"
            self.otherLock = Lock(self.client, self.lock.key)
            self.otherLock.acquire()

        Thread(target=acquire_again).run()
        time.sleep(2)
        expect(self.otherLock).to.not_eq(None)
        expect(hasattr(self.otherLock, 'token')).to.be.false()

    def test_it_should_refresh_the_lock_while_still_being_used(self):
        pass

    def test_it_should_be_usable_as_a_context_manager(self):
        with self.lock as acquired_lock:
            print "Aquired!"
