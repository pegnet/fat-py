import random
import string
from urllib.parse import urljoin

from .errors import handle_error_response
from .session import APISession


class BaseAPI(object):
    def __init__(
        self, ec_address=None, fct_address=None, host=None, username=None, password=None, certfile=None
    ):
        """
        Instantiate a new API client.

        Args:
            ec_address (str): A default entry credit address to use for
                transactions. Credits will be spent from this address.
            fct_address (str): A default factoid address to use for
                transactions.
            host (str): Hostname, including http(s)://, of the node
            username (str): RPC username for protected APIs.
            password (str): RPC password for protected APIs.
            certfile (str): Path to certificate file to verify for TLS
                connections (mostly untested).
        """
        self.ec_address = ec_address
        self.fct_address = fct_address
        self.version = "v1"

        if host:
            self.host = host

        self.session = APISession()

        if username and password:
            self.session.init_basic_auth(username, password)

        if certfile:
            self.session.init_tls(certfile)

    @property
    def url(self):
        return urljoin(self.host, self.version)

    @staticmethod
    def _xact_name():
        return "TX_{}".format("".join(random.choices(string.ascii_uppercase + string.digits, k=6)))

    def _request(self, method, params=None, request_id: int = 0):
        data = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params:
            data["params"] = params

        resp = self.session.request("POST", self.url, json=data)

        if resp.status_code >= 400:
            handle_error_response(resp)

        return resp.json()["result"]


class FATd(BaseAPI):

    def __init__(
        self, ec_address=None, fct_address=None, host=None, username=None, password=None, certfile=None
    ):
        tmp_host = host if host is not None else "http://localhost:8070"
        super().__init__(ec_address, fct_address, tmp_host, username, password, certfile)

    def get_sync_status(self):
        """Retrieve the current sync status of the node."""
        return self._request("get-sync-status")
