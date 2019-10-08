
  
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.models.event import Event
from keckdrpframework.models.processing_context import Processing_context
from keckdrpframework.models.data_set import Data_set

from keckdrpframework.utils.DRPF_logger import getLogger
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.queues import Simple_event_queue, start_queue_manager, get_event_queue, Queue_server

import time



QueuePortNr = 59999
QueueAuthCode = b"testing"
QueueHost = "" 
NItems = 5

QueueManager = None
     
def test_shared_queue_consumer ():    
    # Append items to the shared queue
    queue = get_event_queue(QueueHost, QueuePortNr, QueueAuthCode)    
    
    assert queue is not None, "Failed to connect to queue manager"    
    
    for cnt in range(NItems):
        queue.put (f"Item {cnt}")       
    
    cnt = 0
    ok = True
    while ok:
        try:
            item = queue.get (block=False, timeout=1)
        except:
            print ("here")
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
    

if __name__ == "__main__":
    
    queue = get_event_queue(QueueHost, QueuePortNr, QueueAuthCode)
    
    #manager = get_event_queue(QueueHost, QueuePortNr, QueueAuthCode)    
    
    #manager = get_event_queue(QueueHost, QueuePortNr, QueueAuthCode)
    print ("second")
    test_shared_queue_consumer()
    