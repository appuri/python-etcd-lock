from pyvows import Vows, expect
import etcd
import expectlambda

import os
import sys
sys.path.insert(0, os.path.abspath("."))
from etcdlock import Lock


@Vows.batch
class EtcdLock(Vows.Context):
    def topic(self):
        return etcd.Client()

    def it_should_require_an_etcd_client(self, client):
        expect(lambda: Lock(None, 'lock/foo')).to_raise_error(ValueError)

    def it_should_require_a_valid_ttl(self, client):
        expect(lambda: Lock(client, 'lock/foo', ttl=0)).to_raise_error(ValueError)

    def it_should_require_an_etcd_key(self, client):
        expect(lambda: Lock(client, key=None)).to_raise_error(ValueError)

    class ValidLock(Vows.Context):
        def topic(self, client):
            return (Lock(client, 'lock/foo'), client)

        def it_should_be_usable_as_a_context_manager(self, topic):
            with topic[0] as acquired_lock:
                print "Aquired!"
