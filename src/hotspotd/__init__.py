# @author: Prahlad Yeri
# @description: Initialize hotspotd
# @license: MIT
import argparse
import os
import sys


from .config import (__name__, __description__, __version__, __author__)  # noqa

from .utils import (configure, start_router, stop_router,
                    check_sysfile, is_process_running,
                    install_dir, logging)

logger = logging.getLogger('hotspotd.__init__')


def main():
    parser = argparse.ArgumentParser(
        prog=__name__,
        description=__description__,
        epilog='Refer README.md for more info.')
    parser.add_argument('--version', action='version', version=__version__,
                        help='Show version info')
    parser.add_argument('--debug', required=False, action='store_true')

    # TODO: Also implement `restart`
    parser.add_argument('command', choices=['start', 'stop',
                                            'status', 'configure'])
    args = parser.parse_args()

    if check_sysfile('hostapd') is False:
        sys.exit("hostapd is not installed on your system. \
        This package will not work without it.\nTo install hostapd, \
        run 'sudo apt-get install hostapd'\nor refer to \
        http://wireless.kernel.org/en/users/Documentation/hostapd \
        after this installation gets over.")

    if os.getenv('HOME') != '/root':
        if os.getenv('SUDO_USER') is None:
            sys.exit("You need root permissions to do this, sloth!")

    if args.command == 'configure':
        configure()
    elif args.command == 'status':
        if (is_process_running('hostapd')[0] is False and is_process_running('dnsmasq')[0] is False):  # noqa
            logger.info('hotspotd is STOPPED')
        else:
            logger.info('Either hostapd or dnsmasq or both are running')
    elif args.command == 'stop':
        stop_router()
    elif args.command == 'start':
        if (is_process_running('hostapd') is False or is_process_running('dnsmasq') is False):  # noqa
            logger.info('hotspot is already running')
        else:
            if not os.path.exists(os.path.join(install_dir, 'hotspotd.data')):  # noqa
                configure()
            start_router()
