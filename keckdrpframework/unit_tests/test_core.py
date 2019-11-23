#
# Test core package
#
# Created: 2019-09-26, skwok
#
import pytest

from keckdrpframework.models.arguments import Arguments
from keckdrpframework.models.event import Event
from keckdrpframework.models.processing_context import ProcessingContext
from keckdrpframework.models.data_set import DataSet

from keckdrpframework.utils.drpf_logger import getLogger
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.queues import SimpleEventQueue, get_event_queue, QueueServer, _get_queue_manager, _queue_manager_target

import time
import multiprocessing

#
# Test queues
#

QueuePortNr = 59999
QueueAuthCode = b"testing"
QueueHost = "localhost"
NItems = 5

QueueManager = None


def test_simple_queue():
    eq = SimpleEventQueue()
    for i in range(5):
        eq.put(Arguments(name="test", i=i))
    assert eq.qsize() == 5, "Size mismatch"

    a1 = eq.get()
    a2 = eq.get()
    assert a2.i == 1, "Wrong element queue"


def test_start_queue_server():
    def proc():
        _queue_manager_target(QueueHost, QueuePortNr, QueueAuthCode)

    # Start Queue manager process, which will host the shared queue
    proc = multiprocessing.Process(target=proc)
    proc.start()
    time.sleep (2)
    assert proc is not None, "Could not create queue manager"


def test_shared_queue_producer():
    # Append items to the shared queue
    queue = get_event_queue(QueueHost, QueuePortNr, QueueAuthCode)
    assert queue is not None, "Failed to connect to queue manager"

    for cnt in range(NItems):
        queue.put(f"Item {cnt}")


def test_shared_queue_consumer():
    # Append items to the shared queue
    queue = get_event_queue(QueueHost, QueuePortNr, QueueAuthCode)

    assert queue is not None, "Failed to connect to queue manager"

    cnt = 0
    ok = True
    while ok:
        try:
            item = queue.get(block=False, timeout=3)
        except:
            ok = False
            break
        if item is not None:
            cnt += 1

    assert cnt == NItems, f"Failed to get items from queue, {NItems} expected, got {cnt}"
    try:
        # Kills the queue server process
        queue.terminate()
    except:
        pass


def test_terminate_queue_manager():
    for i in range (5):
        manager = _get_queue_manager(QueueHost, QueuePortNr, QueueAuthCode)
        if manager is not None:
            try:
                queue = manager.get_queue()        
                if queue is not None:
                    queue.terminate()
            except:
                pass
            time.sleep(3)

    assert manager is None, "Terminate failed. Manager still running."
