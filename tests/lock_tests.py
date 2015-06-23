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

class SingleLockTests(unittest.TestCase):
    def setUp(self):
        self.client = etcd.Client()
        self.lock = Lock(self.client, "lock-%d" % random.uniform(1,100000), ttl=2, renewSecondsPrior=1)

    def teardown(self):
        if (self.lock != None and self.lock.token != None):
            self.lock.release()

    def test_it_should_require_an_etcd_client(self):
        expect(lambda: Lock(None, 'lock/foo')).to.raise_error(ValueError)

    def test_it_should_require_a_valid_ttl(self):
        expect(lambda: Lock(self.client, 'lock/foo', ttl=0)).to.raise_error(ValueError)

    def test_it_should_require_a_valid_renew_prior_time(self):
        expect(lambda: Lock(self.client, 'lock/foo', renewSecondsPrior=-5)).to.raise_error(ValueError)

    def test_it_should_require_renew_prior_to_be_less_than_the_ttl(self):
        expect(lambda: Lock(self.client, 'lock/foo', ttl=20, renewSecondsPrior=20)).to.raise_error(ValueError)

    def test_it_should_require_an_etcd_key(self):
        expect(lambda: Lock(self.client, key=None)).to.raise_error(ValueError)

    def test_it_should_be_able_to_be_acquired_and_released(self):
        self.lock = Lock(self.client, "lock-%d" % random.uniform(1,100000))
        self.lock.acquire()
        node = self.client.get(self.lock.key)
        expect(node.value).to.eq(self.lock.token)
        expect(node.ttl).to.eq(60)
        self.lock.release()
        expect(self.client.get(self.lock.key).value).to.eq("0")

    def test_it_should_renew_the_lock_while_still_being_used(self):
        self.lock.acquire()
        time.sleep(2)
        expect(self.client.get(self.lock.key).value).to.eq(self.lock.token)

    def test_it_cancel_the_renew_after_releasing(self):
        self.lock.acquire()
        time.sleep(1)
        self.lock.release()
        time.sleep(3)
        expect(self.client.get(self.lock.key).value).to.eq("0")

    def test_it_should_not_renew_if_renewSecondsPrior_is_None(self):
        self.lock.renewSecondsPrior = None
        self.lock.acquire()
        time.sleep(3)

        expect(lambda: self.client.get(self.lock.key)).to.raise_error(etcd.EtcdKeyNotFound)        

    def test_it_should_be_usable_as_a_context_manager(self):
        with self.lock:
            expect(self.client.get(self.lock.key).value).to.eq(self.lock.token)

        expect(self.client.get(self.lock.key).value).to.eq("0")


class MultipleLocksTests(unittest.TestCase):
    def setUp(self):
        self.client = etcd.Client()
        self.key = "lock-%d" % random.uniform(1,100000)
        self.locks = [
            Lock(etcd.Client(), self.key, ttl=2, renewSecondsPrior=1, name="A"),
            Lock(etcd.Client(), self.key, ttl=3, renewSecondsPrior=1, name="B"),
            Lock(etcd.Client(), self.key, ttl=2, renewSecondsPrior=None, name="C")
        ]

    def teardown(self):
        for lock in self.Locks:
            if (lock != None and lock.token != None):
                lock.release()

    def test_it_should_not_aquire_a_lock_already_acquired(self):
        expect(self.locks[0].acquire()).to.be.true()
        expect(self.locks[1].acquire(timeout=1)).to.be.false()
        expect(self.locks[1].is_locked()).to.be.false()

    def test_it_should_acquire_the_lock_when_another_agent_releases_it(self):
        expect(self.locks[0].acquire()).to.be.true()

        t = Thread(target=lambda: expect(self.locks[1].acquire()).to.be.true())
        t.start()
        time.sleep(1)
        self.locks[0].release()
        t.join()

        expect(self.locks[1].is_locked()).to.be.true()


