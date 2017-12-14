#!/usr/bin/env python
# @author: Prahlad Yeri
# @description: Common functions to interface with linux cli
# @license: MIT

import datetime
import logging
import os
import subprocess  # SimpleHTTPServer,SocketServer

import daiquiri

daiquiri.setup(
    level=logging.DEBUG,
    outputs=(
        daiquiri.output.File('hotspotd_info.log', level=logging.INFO),
        daiquiri.output.File('hotspotd_error.log', level=logging.ERROR),
        daiquiri.output.TimedRotatingFile(
            'hotspotd_debug.log',
            level=logging.DEBUG,
            interval=datetime.timedelta(hours=1))
    )
)

logger = daiquiri.getLogger(__name__)

arguments = None


def get_stdout(pi):
    result = pi.communicate()
    if len(result[0]) > 0:
        return result[0]
    else:
        return result[1]  # some error has occured


def killall(process):
    execute_shell('pkill ' + process)


def execute_shell(command, error=''):
    if arguments.debug:
        logger.debug(command)
    return execute(command, wait=True, shellexec=True, errorstring=error)


def execute(command='', errorstring='', wait=True, shellexec=False, ags=None):
    if arguments.verbose:
        print 'command: ' + command

    try:
        p = subprocess.Popen(command.split(),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if wait and p.wait() == 0:
            return True, p.communicate()[0]
        else:
            return False, p.communicate()[0]
    except subprocess.CalledProcessError as e:
        print 'error occured:' + errorstring
        return errorstring
    except Exception as ea:
        print 'Exception occured:' + ea.message
        return errorstring
        # show_message("Error occured: " + ea.message)


def is_process_running(process):
    cmd = 'pgrep ' + process
    return execute_shell(cmd)


def check_sysfile(filename):
    if os.path.exists('/usr/sbin/' + filename):
        return '/usr/sbin/' + filename
    elif os.path.exists('/sbin/' + filename):
        return '/sbin/' + filename
    else:
        return ''


def get_sysctl(setting):
    result = execute_shell('sysctl ' + setting)
    if '=' in result:
        return result.split('=')[1].lstrip()
    else:
        return result


def set_sysctl(setting, value):
    # We return output here and not status(True, OUTPUT)
    return execute_shell('sysctl -w ' + setting + '=' + value)[1]


def writelog(message):
    if arguments.verbose:
        logger.info(message)
        print(message)
