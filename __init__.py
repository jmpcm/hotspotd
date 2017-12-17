# from .main import configure, start_router, stop_router
from .utils import (configure, start_router, stop_router,
                    check_sysfile, is_process_running, install_dir, logging)
from .cli import main, args

__name__ = "hotspotd"
__description__ = "A simple daemon to create wifi hotspot on Linux!"
__version__ = "0.1.8"
__author__ = "Prahlad Yeri<prahladyeri@yahoo.com>"

__all__ = ['configure', 'start_router', 'stop_router',
           'check_sysfile', 'is_process_running', 'install_dir',
           'main', 'args', 'logging']
