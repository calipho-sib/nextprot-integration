import contextlib
import logging.config
import os
import shutil
import sys
import tempfile

# noinspection PyUnresolvedReferences
import six.moves.urllib_parse as urllib_parse

from taskflow import exceptions
from taskflow.persistence import backends

from oslo_utils import uuidutils
from taskflow.persistence import models

LOG = logging.getLogger(__name__)

try:
    import sqlalchemy as _sa  # noqa
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


def print_wrapped(text):
    print("-" * (len(text)))
    print(text)
    print("-" * (len(text)))


def rm_path(persist_path):
    if not os.path.exists(persist_path):
        return
    if os.path.isdir(persist_path):
        rm_func = shutil.rmtree
    elif os.path.isfile(persist_path):
        rm_func = os.unlink
    else:
        raise ValueError("Unknown how to `rm` path: %s" % (persist_path))
    try:
        rm_func(persist_path)
    except (IOError, OSError):
        pass


def _make_conf(backend_uri):
    parsed_url = urllib_parse.urlparse(backend_uri)
    backend_type = parsed_url.scheme.lower()
    if not backend_type:
        raise ValueError("Unknown backend type for uri: %s" % (backend_type))
    if backend_type in ('file', 'dir'):
        conf = {
            'path': parsed_url.path,
            'connection': backend_uri,
        }
    elif backend_type in ('zookeeper',):
        conf = {
            'path': parsed_url.path,
            'hosts': parsed_url.netloc,
            'connection': backend_uri,
        }
    else:
        conf = {
            'connection': backend_uri,
        }
    return conf


@contextlib.contextmanager
def get_backend(backend_uri=None):
    tmp_dir = None
    if not backend_uri:
        if len(sys.argv) > 1:
            backend_uri = str(sys.argv[1])
        if not backend_uri:
            tmp_dir = tempfile.mkdtemp()
            backend_uri = "file:///%s" % tmp_dir
    try:
        backend = backends.fetch(_make_conf(backend_uri))
    except exceptions.NotFound as e:
        # Fallback to one that will work if the provided backend is not found.
        if not tmp_dir:
            tmp_dir = tempfile.mkdtemp()
            backend_uri = "file:///%s" % tmp_dir
            LOG.exception("Falling back to file backend using temporary"
                          " directory located at: %s", tmp_dir)
            backend = backends.fetch(_make_conf(backend_uri))
        else:
            raise e
    try:
        # Ensure schema upgraded before we continue working.
        with contextlib.closing(backend.get_connection()) as conn:
            conn.upgrade()
        yield backend
    finally:
        # Make sure to cleanup the temporary path if one was created for us.
        if tmp_dir:
            rm_path(tmp_dir)

def print_task_states(flowdetail, msg):
    print_wrapped(msg)
    print("Flow '%s' state: %s" % (flowdetail.name, flowdetail.state))
    # Sort by these so that our test validation doesn't get confused by the
    # order in which the items in the flow detail can be in.
    items = sorted((td.name, td.version, td.state, td.results)
                   for td in flowdetail)
    for item in items:
        print(" %s==%s: %s, result=%s" % item)


def create_log_book_and_flow_details(book_name, backend):

    # Create a place where the persistence information will be stored.
    book = models.LogBook(name=book_name)
    flow_detail = models.FlowDetail("resume from backend "+book_name,
                                    uuid=uuidutils.generate_uuid())
    book.add(flow_detail)
    with contextlib.closing(backend.get_connection()) as conn:
        conn.save_logbook(book)

    return book, flow_detail


def find_flow_detail(backend, lb_id, fd_id):
    conn = backend.get_connection()
    lb = conn.get_logbook(lb_id)
    return lb.find(fd_id)
