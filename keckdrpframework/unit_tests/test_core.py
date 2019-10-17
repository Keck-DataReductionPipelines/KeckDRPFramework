#
# Test core package
#
# Created: 2019-09-26, skwok
#
import pytest

from keckdrpframework.models.arguments import Arguments
from keckdrpframework.models.event import Event
from keckdrpframework.models.processing_context import Processing_context
from keckdrpframework.models.data_set import Data_set

from keckdrpframework.utils.DRPF_logger import getLogger
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.queues import Simple_event_queue, get_event_queue, Queue_server, _get_queue_manager, _queue_manager_target

import time
import multiprocessing

#
# Test queues
#

QueuePortNr = 59999
QueueAuthCode = b"testing"
QueueHost = "" 
NItems = 5

QueueManager = None


def test_simple_queue ():
    eq = Simple_event_queue ()
    for i in range(5):
        eq.put (Arguments(name='test', i=i))    
    assert eq.qsize () == 5, "Size mismatch"
    
    a1 = eq.get()
    a2 = eq.get()
    assert a2.i == 1, "Wrong element queue"
    

def test_start_queue_server ():    
    def proc ():
        _queue_manager_target (QueueHost, QueuePortNr, QueueAuthCode)    

    # Start Queue manager process, which will host the shared queue
    proc = multiprocessing.Process(target=proc)
    proc.start()
    assert proc is not None, "Could not create queue manager"
    
def test_shared_queue_producer ():    
    # Append items to the shared queue    
    queue = get_event_queue(QueueHost, QueuePortNr, QueueAuthCode)
    assert queue is not None, "Failed to connect to queue manager"

    for cnt in range(NItems):
        queue.put (f"Item {cnt}")        
        
def test_shared_queue_consumer ():    
    # Append items to the shared queue
    queue = get_event_queue(QueueHost, QueuePortNr, QueueAuthCode)
    
    assert queue is not None, "Failed to connect to queue manager"    
    
    cnt = 0
    ok = True
    while ok:
        try:
            item = queue.get (block=False, timeout=1)
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
    
def test_terminate_queue_manager ():
    manager = _get_queue_manager (QueueHost, QueuePortNr, QueueAuthCode)
    
    assert manager is None, "Terminate failed. Manager still running."

