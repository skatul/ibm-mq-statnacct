"""
Configuration module for IBM MQ Statistics and Accounting Queue Reader
Contains connection parameters and queue names for MQ operations
"""

# MQ Connection Configuration
MQ_CONFIG = {
    "queue_manager": "MQQM1",
    "channel": "APP1.SVRCONN",
    "connection_name": "localhost(5200)",  # Default MQ port, adjust as needed
    "user": "",  # Set if authentication is required
    "password": ""  # Set if authentication is required
}

# Statistics and Accounting Queue Names
QUEUE_CONFIG = {
    "statistics_queue": "SYSTEM.ADMIN.STATISTICS.QUEUE",
    "accounting_queue": "SYSTEM.ADMIN.ACCOUNTING.QUEUE",
    "command_queue": "SYSTEM.ADMIN.COMMAND.QUEUE"
}

# Statistics Collection Configuration
STATS_CONFIG = {
    "reset_after_read": False,  # Disabled for now - enable when MQ stats are configured
    "collect_queue_stats": True,
    "collect_channel_stats": True,
    "collect_qmgr_stats": True,
    "output_format": "json",
    "include_timestamps": True
}

# Time series database configuration (for future use)
TSDB_CONFIG = {
    "enabled": False,
    "connection_string": "",  # Configure based on your time series DB
    "database_name": "mq_metrics",
    "measurement_name": "mq_statistics"
}