# Licensed under a 3-clause BSD style license - see LICENSE.rst

import time

import astropy.samp.hub as hub_module
import pytest

from astropy.samp import conf
from astropy.samp.hub import SAMPHubServer


def setup_module(module):
    conf.use_internet = False


def test_SAMPHubServer():
    """Test that SAMPHub can be instantiated"""
    SAMPHubServer(web_profile=False, mode="multiple", pool_size=1)


def test_set_xmlrpc_callback_uses_safe_server_proxy():
    hub = SAMPHubServer(web_profile=False, mode="multiple", pool_size=1)
    private_key, public_id = hub._perform_standard_register()

    try:
        hub._set_xmlrpc_callback(private_key, "http://127.0.0.1:8000")
        endpoint = hub._xmlrpc_endpoints[public_id][1]
        proxy = endpoint._proxies.get_nowait()
        endpoint._proxies.put(proxy)
        assert proxy.__class__ is hub_module.defused_xmlrpc.ServerProxy
    finally:
        hub._xmlrpc_endpoints[public_id][1].shutdown()


@pytest.mark.slow
def test_SAMPHubServer_run():
    """Test that SAMPHub can be run"""
    hub = SAMPHubServer(web_profile=False, mode="multiple", pool_size=1)
    hub.start()
    time.sleep(1)
    hub.stop()


@pytest.mark.slow
def test_SAMPHubServer_run_repeated():
    """
    Test that SAMPHub can be restarted after it has been stopped, including
    when web profile support is enabled.
    """

    hub = SAMPHubServer(web_profile=True, mode="multiple", pool_size=1)
    hub.start()
    time.sleep(1)
    hub.stop()
    time.sleep(1)
    hub.start()
    time.sleep(1)
    hub.stop()
