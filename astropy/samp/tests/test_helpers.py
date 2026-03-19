import os
import pickle
import random
import string
import time

import astropy.samp.lockfile_helpers as lockfile_helpers
from astropy.samp import SAMP_STATUS_OK
from astropy.samp.lockfile_helpers import check_running_hub

TEST_REPLY = {"samp.status": SAMP_STATUS_OK, "samp.result": {"txt": "test"}}


def write_output(mtype, private_key, sender_id, params):
    filename = params["verification_file"]
    f = open(filename, "wb")
    pickle.dump(mtype, f)
    pickle.dump(private_key, f)
    pickle.dump(sender_id, f)
    pickle.dump(params, f)
    f.close()


def assert_output(mtype, private_key, sender_id, params, timeout=None):
    filename = params["verification_file"]
    start = time.time()
    while True:
        try:
            with open(filename, "rb") as f:
                rec_mtype = pickle.load(f)
                rec_private_key = pickle.load(f)
                rec_sender_id = pickle.load(f)
                rec_params = pickle.load(f)
            break
        except (OSError, EOFError):
            if timeout is not None and time.time() - start > timeout:
                raise Exception(f"Timeout while waiting for file: {filename}")

    assert rec_mtype == mtype
    assert rec_private_key == private_key
    assert rec_sender_id == sender_id
    assert rec_params == params


class Receiver:
    def __init__(self, client):
        self.client = client

    def receive_notification(self, private_key, sender_id, mtype, params, extra):
        write_output(mtype, private_key, sender_id, params)

    def receive_call(self, private_key, sender_id, msg_id, mtype, params, extra):
        # Here we need to make sure that we first reply, *then* write out the
        # file, otherwise the tests see the file and move to the next call
        # before waiting for the reply to be received.
        self.client.reply(msg_id, TEST_REPLY)
        self.receive_notification(private_key, sender_id, mtype, params, extra)

    def receive_response(self, private_key, sender_id, msg_id, response):
        pass


def random_id(length=16):
    return "".join(random.sample(string.ascii_letters + string.digits, length))


def random_params(directory):
    return {
        "verification_file": os.path.join(directory, random_id()),
        "parameter1": "abcde",
        "parameter2": 1331,
    }


def test_check_running_hub_uses_safe_server_proxy(monkeypatch, tmp_path):
    recorded = {}
    lockfile = tmp_path / ".samp"
    lockfile.write_text("samp.hub.xmlrpc.url=http://127.0.0.1:8000\n")

    class SafeProxy:
        def __init__(self, *args, **kwargs):
            recorded["called"] = True

        @property
        def samp(self):
            class Hub:
                @staticmethod
                def ping():
                    return None

            class Samp:
                hub = Hub()

            return Samp()

    monkeypatch.setattr(lockfile_helpers.defused_xmlrpc, "ServerProxy", SafeProxy)

    is_running, _ = check_running_hub(str(lockfile))

    assert is_running
    assert recorded["called"]
