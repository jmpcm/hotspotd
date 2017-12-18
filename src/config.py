__name__ = 'hotspotd'
__version__ = '0.1.8'
__description__ = 'Simple daemon to create a wifi hotspot on GNU/Linux'
__author__ = "Prahlad Yeri <prahladyeri@yahoo.com>"


log_config = {
    'disable_existing_loggers': False,
    'version': 1,
    'formatters': {
        'long': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'
        },
        'short': {
            'format': '%(levelname)s: %(message)s'
        },
        'cli': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'cli',
            'class': 'logging.StreamHandler',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'long',
            'filename': '/var/log/hotspotd.log',
            'maxBytes': 5 * (1024 ** 2),
            'backupCount': 5
        },
    },
    'loggers': {
        '': {
            'handlers': ['file_debug'],
            'level': 'DEBUG',
        },
        'hotspotd.__init__': {
            'handlers': ['console'],
            'level': 'INFO',
            'propogate': False,
        },
        'hotspotd.utils': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propogate': False,
        },
    },
}
