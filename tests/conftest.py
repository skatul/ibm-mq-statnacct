"""
Test configuration and fixtures for IBM MQ Statistics Reader tests.
"""

import sys
import os
import pytest

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class MockPymqi:
    """Mock pymqi module for testing without actual MQ connection"""
    
    class CMQC:
        # Connection constants
        MQCHT_CLNTCONN = 6
        MQXPT_TCP = 1
        
        # Queue constants
        MQOO_OUTPUT = 0x00000010
        MQOO_INPUT_AS_Q_DEF = 0x00000001
        MQOO_BROWSE = 0x00000008
        MQOO_INQUIRE = 0x00000020
        
        # Message constants
        MQFMT_STRING = b'MQSTR   '
        
        # Get message options
        MQGMO_NO_WAIT = 0x00000001
        MQGMO_FAIL_IF_QUIESCING = 0x00002000
        MQGMO_BROWSE_FIRST = 0x00000010
        MQGMO_BROWSE_NEXT = 0x00000020
        
        # Return codes
        MQRC_NO_MSG_AVAILABLE = 2033
        MQRC_UNKNOWN_OBJECT_NAME = 2085
        MQRC_NOT_AUTHORIZED = 2035
        
        # Queue types
        MQQT_LOCAL = 1
        
        # Statistics constants
        MQCA_Q_NAME = 2016
        MQIA_GET_COUNT = 3004
        MQIA_PUT_COUNT = 3003
        MQIA_BROWSE_COUNT = 3007
        MQMON_ON = 1
        MQMON_ENABLED = 1
    
    class CMQCFC:
        MQCACH_CHANNEL_NAME = 1501
    
    class CD:
        def __init__(self):
            self.ChannelName = b''
            self.ConnectionName = b''
            self.ChannelType = 0
            self.TransportType = 0
            self.UserIdentifier = b''
            self.Password = b''
    
    class MD:
        def __init__(self):
            self.MsgId = b'12345678901234567890123456789012'
            self.CorrelId = b'12345678901234567890123456789012'
            self.PutDate = '20251108'
            self.PutTime = '13000000'
            self.Format = b'        '
    
    class GMO:
        def __init__(self):
            self.Options = 0
    
    class Queue:
        def __init__(self, qmgr, queue_name, open_options=None):
            self.qmgr = qmgr
            self.queue_name = queue_name
            self.open_options = open_options
            self._messages = []
            self._closed = False
        
        def put(self, message, md):
            if self._closed:
                raise MockPymqi.MQMIError(2018, 2)  # Queue not open for output
            self._messages.append((message, md))
        
        def get(self, buffer, md, gmo):  # pylint: disable=unused-argument
            if self._closed:
                raise MockPymqi.MQMIError(2018, 2)  # Queue not open for input
            if not self._messages:
                raise MockPymqi.MQMIError(MockPymqi.CMQC.MQRC_NO_MSG_AVAILABLE, 2)
            message, orig_md = self._messages.pop(0)
            # Copy message descriptor properties
            md.MsgId = orig_md.MsgId if hasattr(orig_md, 'MsgId') else b'12345678901234567890123456789012'
            return message
        
        def close(self):
            self._closed = True
    
    class QueueManager:
        def __init__(self, name):
            self.name = name
            self._connected = False
        
        def connect_with_options(self, qm_name, cd):  # pylint: disable=unused-argument
            self._connected = True
        
        def disconnect(self):
            self._connected = False
    
    class PCFExecute:
        def __init__(self, qmgr):
            self.qmgr = qmgr
        
        def MQCMD_RESET_Q_STATS(self, args):
            pass
        
        def MQCMD_RESET_CHANNEL_STATS(self, args):
            pass
    
    class MQMIError(Exception):
        def __init__(self, reason, comp):
            self.reason = reason
            self.comp = comp
            super().__init__(f"MQI Error. Comp: {comp}, Reason: {reason}")


@pytest.fixture
def mock_pymqi(monkeypatch):
    """Fixture to mock pymqi module"""
    mock_module = MockPymqi()
    monkeypatch.setattr('sys.modules', {**sys.modules, 'pymqi': mock_module})
    return mock_module


@pytest.fixture
def sample_pcf_message():
    """Sample PCF message bytes for testing"""
    # Create a minimal PCF header (36 bytes) + some parameters
    header = bytearray(36)
    header[0:4] = (21).to_bytes(4, 'big')  # MQCFT_STATISTICS
    header[4:8] = (36).to_bytes(4, 'big')  # Structure length
    header[8:12] = (1).to_bytes(4, 'big')  # Version
    header[12:16] = (150).to_bytes(4, 'big')  # Command
    header[32:36] = (2).to_bytes(4, 'big')  # Parameter count
    
    # Add some sample parameters
    param1 = bytearray(20)  # Parameter header + string value
    param1[0:4] = (2016).to_bytes(4, 'big')  # MQCA_Q_NAME
    param1[4:8] = (4).to_bytes(4, 'big')    # String type
    param1[8:12] = (8).to_bytes(4, 'big')   # String length
    param1[12:20] = b'APP1.REQ'
    
    param2 = bytearray(12)  # Parameter header + integer value
    param2[0:4] = (3004).to_bytes(4, 'big')  # MQIA_GET_COUNT
    param2[4:8] = (3).to_bytes(4, 'big')    # Integer type
    param2[8:12] = (25).to_bytes(4, 'big')  # Value
    
    return bytes(header + param1 + param2)


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'MQ_CONFIG': {
            'queue_manager': 'TEST_QM',
            'channel': 'TEST.SVRCONN',
            'connection_name': 'localhost(1414)',
            'user': 'testuser',
            'password': 'testpass'
        },
        'QUEUE_CONFIG': {
            'statistics_queue': 'SYSTEM.ADMIN.STATISTICS.QUEUE',
            'accounting_queue': 'SYSTEM.ADMIN.ACCOUNTING.QUEUE',
            'command_queue': 'SYSTEM.ADMIN.COMMAND.QUEUE'
        },
        'STATS_CONFIG': {
            'reset_after_read': False,
            'collect_queue_stats': True,
            'collect_channel_stats': True,
            'collect_qmgr_stats': True,
            'output_format': 'json',
            'include_timestamps': True
        }
    }