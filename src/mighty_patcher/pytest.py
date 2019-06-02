import inspect
import pytest
from _pytest.runner import CallInfo
from _pytest.debugging import _enter_pdb

import warnings

from mighty_patcher.watch import AutoReloader


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption('--reload-loop',
                    action='store_true',
                    help="When a test fails set up a reload loop ")
    group.addoption('--reload-dir',
                    help="Base directory to set up the auto-reloader to")

def pytest_collection_modifyitems(session, config, items):
    if config.option.reload_loop:
        path = config.option.reload_dir or config.invocation_dir
        session.auto_reloader = AutoReloader(path)


@pytest.hookimpl(hookwrapper=True)
def pytest_pyfunc_call(pyfuncitem):
    if not pyfuncitem.config.option.reload_loop:
        yield
    else:
        testfunction = pyfuncitem.obj
        iscoroutinefunction = getattr(inspect, "iscoroutinefunction", None)
        if iscoroutinefunction is not None and iscoroutinefunction(testfunction):
            msg = "Coroutine functions are not natively supported and have been skipped.\n"
            msg += "You need to install a suitable plugin for your async framework, for example:\n"
            msg += "  - pytest-asyncio\n"
            msg += "  - pytest-trio\n"
            msg += "  - pytest-tornasync"
            warnings.warn(pytest.PytestWarning(msg.format(pyfuncitem.nodeid)))
            pytest.skip(msg="coroutine function and no async plugin installed (see warnings)")
        funcargs = pyfuncitem.funcargs
        testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
        passing = False
        while not passing:
            info = CallInfo.from_call(
                lambda: testfunction(**testargs),
                when="call",
                reraise=None
            )
            # if info.excinfo:
            if info.excinfo:
                # build the pytest report
                report = pyfuncitem.ihook.pytest_runtest_makereport(
                    item=pyfuncitem,
                    call=info
                )
                _enter_pdb(pyfuncitem, info.excinfo, report)
            else:
                passing = True
        # after you've successfully gotten the test to pass run it one more time
        # (this hack exists because of the hookwrapper logic)
        yield
