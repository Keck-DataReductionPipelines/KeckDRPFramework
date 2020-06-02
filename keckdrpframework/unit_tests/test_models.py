#
# Test models package
#
# Created: 2019-09-26, skwok
#
import pytest
import sys

sys.path.append("../..")


from keckdrpframework.models.arguments import Arguments
from keckdrpframework.models.event import Event
from keckdrpframework.models.processing_context import ProcessingContext
from keckdrpframework.models.data_set import DataSet

from keckdrpframework.utils.drpf_logger import getLogger
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.queues import SimpleEventQueue

import time


#
# Arguments tests
#


def test_arguments_1():
    args = Arguments(name="test", a=1, b=2, c="3")

    assert args.a == 1 and args.b == 2 and args.c == "3", "Arguments do not  match"


def test_arguments_2():
    args = Arguments(name="test", a=1, b=2, c="3")

    s = args.__str__()

    assert s == '"name": test, "a": 1, "b": 2, "c": 3', "Arguments str() failed"


def test_arguments_3():
    args = Arguments(4, 7, 19, name="test", a=1, c="3")
    assert args[0] == 4 and args[2] == 19 and args["a"] == 1, "Arguments: constructor failed"

    assert len(args) == 3, f"Arguments: len returns wrong value ({len(args)}, should be 3)"
    args_iter = iter(args)
    for ix in range(len(args)):
        assert next(args_iter) == args[ix], "Arguments: Iteration doesn't match index"
    try:
        val = next(args_iter)
    except StopIteration:
        pass
    except Exception:
        assert False, "Arguments: unexpected exception on iteration"
    else:
        assert False, "Arguments: Expected StopIteration exception not raised"

    assert args.len_kw() == 3, f"Arguments: len_kw returns wrong value ({args.len_kw()}, should be 3"
    args_iter_kw = args.iter_kw()
    val = next(args_iter_kw)
    assert val == "name" and args[val] == "test", "Arguments: keyword iteration does not match"
    val = next(args_iter_kw)
    assert val == "a" and args[val] == 1, "Arguments: keyword iteration does not match (2)"
    val = next(args_iter_kw)
    assert val == "c" and args[val] == "3", "Arguments: keyword iteration does not match (3)"
    try:
        val = next(args_iter_kw)
    except StopIteration:
        pass
    except Exception:
        assert False, "Arguments, unexpected exception"
    else:
        assert False, "Arguments: Expected StopIteration exception not raised"

    args.insert(0, 1)
    assert len(args) == 4 and args[0] == 1 and args[2] == 7, "Arguments: insert failed"

    val = args.pop()
    assert len(args) == 3 and val == 19, "Arguments: pop failed"

    args.append(24)
    assert len(args) == 4 and args[3] == 24, "Arguments: append failed"

    args.extend(5, 6, 7)
    assert len(args) == 7 and args[4] == 5 and args[6] == 7, "Arguments: extend failed"

    args.update(d="D", e="E")
    assert args.len_kw() == 5 and args.d == "D", "Arguments: update failed"


#
# Processing context tests
#


@pytest.fixture
def init_context():
    config = ConfigClass()
    logger = getLogger(config.logger_config_file, name="DRPF")
    eq = SimpleEventQueue()
    eqhi = SimpleEventQueue()

    # The regular event queue can be local or shared via proxy manager
    pc = ProcessingContext(eq, eqhi, logger, config)
    return pc


def test_context_new(init_context):
    """
    Context creation
    """
    pc = init_context
    assert pc is not None, "No context created"


def test_append_new_event(init_context):
    """
    Append new event 
    """
    pc = init_context
    pc.append_new_event("test", Arguments("test", a=1))
    pc.append_new_event("test1", Arguments("test1", a=2))
    pc.append_new_event("test2", Arguments("test2", a=3))

    e1 = pc.event_queue.get()
    e2 = pc.event_queue.get()
    e3 = pc.event_queue.get()
    assert e1.args.a == 1 and e2.args.a == 2 and e3.args.a == 3, "Unexpected event arguments"


#
# DataSet tests
#


@pytest.fixture
def init_data_set():
    config = ConfigClass()
    logger = getLogger(config.logger_config_file, name="DRPF")

    data_set = DataSet("test_files", logger, config, SimpleEventQueue())
    return data_set


def test_data_set_1(init_data_set):
    """
    Creation
    """
    data_set = init_data_set
    assert data_set is not None, "Could not create data set"


def test_data_set_start(init_data_set):
    data_set = init_data_set
    data_set.start_monitor()


def test_data_set_get_info(init_data_set):
    data_set = init_data_set

    fname0 = data_set.data_table.index[0]
    info0 = data_set.get_info(fname0)
    targname0 = info0.get("TARGNAME")

    targname1 = data_set.get_info_column(fname0, "TARGNAME")
    assert targname0 == targname1, "Target names do not match"


def test_data_set_stop(init_data_set):
    data_set = init_data_set
    time.sleep(2)
    data_set.stop_monitor()
