"""
IBM MQ Constants for PCF (Programmable Command Format) Message Parsing

Based on the IBM MQ Go implementation reference:
https://github.com/skatul/ibmmq-go-stat-otel

These constants are used for parsing PCF messages from IBM MQ statistics and accounting queues.
"""

# PCF Command Format Types (MQCFT_*)
MQCFT_NONE = 0
MQCFT_COMMAND = 1
MQCFT_RESPONSE = 2
MQCFT_INTEGER = 3
MQCFT_STRING = 4
MQCFT_INTEGER_LIST = 5
MQCFT_STRING_LIST = 6
MQCFT_EVENT = 7
MQCFT_USER = 8
MQCFT_BYTE_STRING = 9
MQCFT_TRACE_ROUTE = 10
MQCFT_REPORT = 11
MQCFT_INTEGER_FILTER = 12
MQCFT_STRING_FILTER = 13
MQCFT_BYTE_STRING_FILTER = 14
MQCFT_COMMAND_XR = 16
MQCFT_XR_MSG = 17
MQCFT_XR_ITEM = 18
MQCFT_XR_SUMMARY = 19
MQCFT_GROUP = 20
MQCFT_STATISTICS = 21
MQCFT_ACCOUNTING = 22

# Statistics Types (MQCMD_*)
MQCMD_STATISTICS_MQI = 112      # 0x70
MQCMD_STATISTICS_Q = 113        # 0x71
MQCMD_STATISTICS_CHANNEL = 114  # 0x72

# Accounting Types (MQCMD_*)
MQCMD_ACCOUNTING_MQI = 138      # 0x8A
MQCMD_ACCOUNTING_Q = 139        # 0x8B

# Common Parameters (MQCA_*, MQIA_*) - corrected based on Go reference
MQCA_Q_NAME = 2016              # Queue name
MQCA_Q_MGR_NAME = 2002          # Queue manager name
MQCA_CHANNEL_NAME = 3501        # Channel name
MQCA_CONNECTION_NAME = 3502     # Connection name
MQCA_APPL_NAME = 2024           # Application name

# Queue Attributes (MQIA_*)
MQIA_Q_TYPE = 20                # Queue type
MQIA_CURRENT_Q_DEPTH = 3        # Current queue depth
MQIA_OPEN_INPUT_COUNT = 65      # Open input count
MQIA_OPEN_OUTPUT_COUNT = 66     # Open output count

# Queue Statistics (MQIA_*)
MQIA_HIGH_Q_DEPTH = 36          # High queue depth
MQIA_MSG_DEQ_COUNT = 38         # Messages dequeued (GET count)
MQIA_MSG_ENQ_COUNT = 37         # Messages enqueued (PUT count)

# Channel Statistics (MQIACH_*)
MQIACH_MSGS = 1501              # Channel messages
MQIACH_BYTES = 1502             # Channel bytes
MQIACH_BATCHES = 1503           # Channel batches

# MQI Statistics (MQIAMO_*) - Note: some IDs conflict with MQIA_*, prioritizing MQIA_*
MQIAMO_OPENS = 10003            # MQI opens (avoiding conflict with MQIA_CURRENT_Q_DEPTH)
MQIAMO_CLOSES = 4               # MQI closes
MQIAMO_PUTS = 17                # MQI puts
MQIAMO_GETS = 18                # MQI gets
MQIAMO_COMMITS = 12             # MQI commits
MQIAMO_BACKOUTS = 13            # MQI backouts

# Time and Control Parameters (MQCACF_*, MQIACF_*)
MQCACF_COMMAND_TIME = 3603      # Command time
MQIACF_SEQUENCE_NUMBER = 1001   # Sequence number

# Parameter ID to Name Mapping - corrected based on Go reference
PARAMETER_NAMES = {
    # Common Parameters
    MQCA_Q_NAME: 'MQCA_Q_NAME',
    MQCA_Q_MGR_NAME: 'MQCA_Q_MGR_NAME',
    MQCA_CHANNEL_NAME: 'MQCA_CHANNEL_NAME',
    MQCA_CONNECTION_NAME: 'MQCA_CONNECTION_NAME',
    MQCA_APPL_NAME: 'MQCA_APPL_NAME',
    
    # Queue Attributes
    MQIA_Q_TYPE: 'MQIA_Q_TYPE',
    MQIA_CURRENT_Q_DEPTH: 'MQIA_CURRENT_Q_DEPTH',
    MQIA_OPEN_INPUT_COUNT: 'MQIA_OPEN_INPUT_COUNT',
    MQIA_OPEN_OUTPUT_COUNT: 'MQIA_OPEN_OUTPUT_COUNT',
    
    # Queue Statistics
    MQIA_HIGH_Q_DEPTH: 'MQIA_HIGH_Q_DEPTH',
    MQIA_MSG_DEQ_COUNT: 'MQIA_MSG_DEQ_COUNT',
    MQIA_MSG_ENQ_COUNT: 'MQIA_MSG_ENQ_COUNT',
    
    # Channel Statistics
    MQIACH_MSGS: 'MQIACH_MSGS',
    MQIACH_BYTES: 'MQIACH_BYTES',
    MQIACH_BATCHES: 'MQIACH_BATCHES',
    
    # MQI Statistics
    10003: 'MQIAMO_OPENS',  # Avoiding conflict with MQIA_CURRENT_Q_DEPTH (3)
    MQIAMO_CLOSES: 'MQIAMO_CLOSES',
    MQIAMO_PUTS: 'MQIAMO_PUTS',
    MQIAMO_GETS: 'MQIAMO_GETS',
    MQIAMO_COMMITS: 'MQIAMO_COMMITS',
    MQIAMO_BACKOUTS: 'MQIAMO_BACKOUTS',
    
    # Time and Control Parameters
    MQCACF_COMMAND_TIME: 'MQCACF_COMMAND_TIME',
    MQIACF_SEQUENCE_NUMBER: 'MQIACF_SEQUENCE_NUMBER',
    
    # Additional commonly seen parameters
    2001: 'MQCA_Q_NAME_ALT',
    2003: 'MQCA_PROCESS_NAME',
    2004: 'MQCA_TRIGGER_DATA',
    2005: 'MQCA_Q_DESC',
    2006: 'MQCA_CREATION_DATE',
    2007: 'MQCA_CREATION_TIME',
    2008: 'MQCA_ALTERATION_DATE',
    2009: 'MQCA_ALTERATION_TIME',
    2010: 'MQCA_BACKOUT_REQ_Q_NAME',
    2011: 'MQCA_INITIATION_Q_NAME',
    2012: 'MQCA_DEAD_LETTER_Q_NAME',
    2013: 'MQCA_DEF_XMIT_Q_NAME',
    2014: 'MQCA_CF_STRUC_NAME',
    2015: 'MQCA_QSG_NAME',
    2017: 'MQCA_XCFGNAME',
    2018: 'MQCA_XCFMNAME',
    2019: 'MQCA_COMMAND_MQSC',
    2020: 'MQCA_Q_MGR_IDENTIFIER',
    2021: 'MQCA_CLUSTER_NAME',
    2022: 'MQCA_CLUSTER_NAMELIST',
    2023: 'MQCA_CLUSTER_Q_MGR_NAME',
    
    # Integer attributes (MQIA_*) - fix conflict between constants
    1: 'MQIA_Q_TYPE_ALT',
    2: 'MQIA_MAX_Q_DEPTH',
    # Note: ID 3 is handled by MQIA_CURRENT_Q_DEPTH constant above
    4: 'MQIA_BACKOUT_THRESHOLD',
    5: 'MQIA_SHAREABILITY',
    6: 'MQIA_DEF_SHAREABILITY',
    7: 'MQIA_HARDEN_GET_BACKOUT',
    8: 'MQIA_MSG_DELIVERY_SEQUENCE',
    9: 'MQIA_RETENTION_INTERVAL',
    10: 'MQIA_Q_DEPTH_HIGH_EVENT',
    11: 'MQIA_Q_DEPTH_LOW_EVENT',
    12: 'MQIA_Q_SERVICE_INTERVAL_EVENT',
    13: 'MQIA_Q_DEPTH_MAX_EVENT',
    14: 'MQIA_CURRENT_Q_DEPTH_ALT',
    15: 'MQIA_OPEN_INPUT_COUNT_ALT',
    16: 'MQIA_OPEN_OUTPUT_COUNT_ALT',
    17: 'MQIA_HIGH_Q_DEPTH_ALT',
    18: 'MQIA_MSG_ENQ_COUNT_ALT',
    19: 'MQIA_MSG_DEQ_COUNT_ALT',
    
    # Channel integer attributes (MQIACH_*)
    1501: 'MQIACH_CHANNEL_TYPE',
    1502: 'MQIACH_TRANSPORT_TYPE',
    1503: 'MQIACH_DATA_COUNT',
    1504: 'MQIACH_NAME_COUNT',
    1505: 'MQIACH_MAX_MSG_LENGTH',
    1506: 'MQIACH_BATCH_SIZE',
    1507: 'MQIACH_BATCH_INTERVAL',
    1508: 'MQIACH_LONG_RETRY_COUNT',
    1509: 'MQIACH_LONG_RETRY_INTERVAL',
    1510: 'MQIACH_SHORT_RETRY_COUNT',
    1511: 'MQIACH_SHORT_RETRY_INTERVAL',
    1512: 'MQIACH_DISC_INTERVAL',
    1513: 'MQIACH_THRESHOLD',
    1514: 'MQIACH_PRIORITY',
    1515: 'MQIACH_DATA_CONVERSION',
}

# Channel Type Names
CHANNEL_TYPES = {
    1: 'SENDER',
    2: 'SERVER',
    3: 'RECEIVER',
    4: 'REQUESTER',
    5: 'CLIENT_CONNECTION',
    6: 'SERVER_CONNECTION',
    7: 'CLUSTER_RECEIVER',
    8: 'CLUSTER_SENDER'
}

# Transport Type Names
TRANSPORT_TYPES = {
    1: 'LU62',
    2: 'TCP',
    3: 'NETBIOS',
    4: 'SPX',
    5: 'DECnet',
    6: 'UDP'
}

# Channel Status Names
CHANNEL_STATUSES = {
    0: 'INACTIVE',
    1: 'BINDING',
    2: 'STARTING',
    3: 'RUNNING',
    4: 'STOPPING',
    5: 'RETRYING',
    6: 'STOPPED',
    7: 'REQUESTING',
    8: 'PAUSED',
    13: 'INITIALIZING'
}

# Message Type Mapping
MESSAGE_TYPES = {
    MQCFT_STATISTICS: 'statistics',
    MQCFT_ACCOUNTING: 'accounting',
    MQCFT_EVENT: 'event',
    MQCFT_COMMAND: 'command',
    MQCFT_RESPONSE: 'response',
    MQCFT_REPORT: 'report'
}

def get_parameter_name(param_id: int) -> str:
    """Get human-readable parameter name from parameter ID"""
    return PARAMETER_NAMES.get(param_id, f'UNKNOWN_PARAM_{param_id}_0x{param_id:08X}')

def get_message_type(structure_type: int) -> str:
    """Determine the type of PCF message based on structure type"""
    return MESSAGE_TYPES.get(structure_type, f'unknown_type_{structure_type}')

def get_channel_type_name(channel_type: int) -> str:
    """Convert channel type integer to readable name"""
    return CHANNEL_TYPES.get(channel_type, f'UNKNOWN_CHANNEL_TYPE_{channel_type}')

def get_transport_type_name(transport_type: int) -> str:
    """Convert transport type integer to readable name"""
    return TRANSPORT_TYPES.get(transport_type, f'UNKNOWN_TRANSPORT_{transport_type}')

def get_channel_status_name(status: int) -> str:
    """Convert channel status integer to readable name"""
    return CHANNEL_STATUSES.get(status, f'UNKNOWN_STATUS_{status}')