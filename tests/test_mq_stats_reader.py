"""
Test cases for MQ Stats Reader module.
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import after adding path
from mq_stats_reader import MQStatsReader


class TestMQStatsReader:
    """Test cases for MQ Stats Reader"""

    def setup_method(self):
        """Set up test fixtures"""
        # Mock pymqi before importing
        self.mock_pymqi = MagicMock()
        sys.modules['pymqi'] = self.mock_pymqi
        
        # Mock config
        self.mock_config = {
            'MQ_CONFIG': {
                'queue_manager': 'TEST_QM',
                'channel': 'TEST.SVRCONN',
                'connection_name': 'localhost(1414)',
                'user': 'testuser',
                'password': 'testpass'
            },
            'QUEUE_CONFIG': {
                'statistics_queue': 'SYSTEM.ADMIN.STATISTICS.QUEUE',
                'accounting_queue': 'SYSTEM.ADMIN.ACCOUNTING.QUEUE'
            },
            'STATS_CONFIG': {
                'reset_after_read': False,
                'collect_queue_stats': True,
                'output_format': 'json'
            }
        }
        
        # Patch modules before using
        self.patcher_config = patch.dict(sys.modules, {
            'config': MagicMock(**self.mock_config),
            'pcf_parser': MagicMock()
        })
        self.patcher_config.start()

    def teardown_method(self):
        """Clean up after each test"""
        if hasattr(self, 'patcher_config'):
            self.patcher_config.stop()

    def test_reader_initialization(self):
        """Test MQ stats reader initialization"""
        reader = MQStatsReader()
        assert reader is not None
        assert hasattr(reader, 'qmgr')
        assert hasattr(reader, 'logger')
        assert hasattr(reader, 'pcf_parser')

    @patch('sys.modules')
    def test_connect_to_mq_success(self, mock_modules):
        """Test successful MQ connection"""
        # Setup mocks
        mock_qmgr = MagicMock()
        mock_cd = MagicMock()
        
        mock_modules.__setitem__('pymqi', self.mock_pymqi)
        mock_modules.__setitem__('config', MagicMock(**self.mock_config))
        mock_modules.__setitem__('pcf_parser', MagicMock())
        
        self.mock_pymqi.CD.return_value = mock_cd
        self.mock_pymqi.QueueManager.return_value = mock_qmgr
        self.mock_pymqi.CMQC.MQCHT_CLNTCONN = 6
        self.mock_pymqi.CMQC.MQXPT_TCP = 1
        
        reader = MQStatsReader()
        result = reader.connect_to_mq()
        
        assert result is True
        assert reader.qmgr == mock_qmgr

    @patch('sys.modules')
    def test_connect_to_mq_failure(self, mock_modules):
        """Test MQ connection failure"""
        mock_modules.__setitem__('pymqi', self.mock_pymqi)
        mock_modules.__setitem__('config', MagicMock(**self.mock_config))
        mock_modules.__setitem__('pcf_parser', MagicMock())
        
        # Setup MQMIError
        mock_error = Exception("Connection failed")
        self.mock_pymqi.MQMIError = mock_error
        self.mock_pymqi.QueueManager.side_effect = mock_error
        
        reader = MQStatsReader()
        result = reader.connect_to_mq()
        
        assert result is False

    @patch('sys.modules')
    def test_read_statistics_queue_empty(self, mock_modules):
        """Test reading empty statistics queue"""
        mock_queue = MagicMock()
        mock_queue.get.side_effect = self.mock_pymqi.MQMIError(2033, 2)  # No messages
        
        mock_modules.__setitem__('pymqi', self.mock_pymqi)
        mock_modules.__setitem__('config', MagicMock(**self.mock_config))
        mock_modules.__setitem__('pcf_parser', MagicMock())
        
        self.mock_pymqi.Queue.return_value = mock_queue
        self.mock_pymqi.CMQC.MQRC_NO_MSG_AVAILABLE = 2033
        
        reader = MQStatsReader()
        reader.qmgr = MagicMock()
        
        result = reader.read_statistics_queue()
        assert isinstance(result, list)
        assert len(result) == 0

    @patch('sys.modules')
    def test_read_statistics_queue_with_messages(self, mock_modules):
        """Test reading statistics queue with messages"""
        mock_queue = MagicMock()
        mock_md = MagicMock()
        mock_md.MsgId = b'12345678901234567890123456789012'
        mock_md.CorrelId = b'12345678901234567890123456789012'
        mock_md.PutDate = '20251108'
        mock_md.PutTime = '13000000'
        
        # First call returns message, second raises no message available
        mock_queue.get.side_effect = [
            b'sample_pcf_message_data',
            self.mock_pymqi.MQMIError(2033, 2)
        ]
        
        mock_modules.__setitem__('pymqi', self.mock_pymqi)
        mock_modules.__setitem__('config', MagicMock(**self.mock_config))
        mock_pcf_parser = MagicMock()
        mock_modules.__setitem__('pcf_parser', mock_pcf_parser)
        
        self.mock_pymqi.Queue.return_value = mock_queue
        self.mock_pymqi.MD.return_value = mock_md
        self.mock_pymqi.GMO.return_value = MagicMock()
        self.mock_pymqi.CMQC.MQRC_NO_MSG_AVAILABLE = 2033
        
        reader = MQStatsReader()
        reader.qmgr = MagicMock()
        
        result = reader.read_statistics_queue()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_format_output(self):
        """Test output formatting"""
        with patch.dict(sys.modules, {
            'config': MagicMock(**self.mock_config),
            'pcf_parser': MagicMock()
        }):
            reader = MQStatsReader()
            
            stats_data = [{'message_type': 'statistics', 'queue_name': 'TEST.QUEUE'}]
            accounting_data = [{'message_type': 'accounting', 'channel_name': 'TEST.SVRCONN'}]
            
            result = reader.format_output(stats_data, accounting_data)
            
            assert isinstance(result, str)
            parsed_result = json.loads(result)
            assert 'collection_info' in parsed_result
            assert 'statistics_data' in parsed_result
            assert 'accounting_data' in parsed_result
            assert 'summary' in parsed_result
            assert parsed_result['collection_info']['statistics_count'] == 1
            assert parsed_result['collection_info']['accounting_count'] == 1

    def test_generate_summary(self):
        """Test summary generation"""
        with patch.dict(sys.modules, {
            'config': MagicMock(**self.mock_config),
            'pcf_parser': MagicMock()
        }):
            reader = MQStatsReader()
            
            stats_data = [
                {'statistics_type': 'queue_statistics'},
                {'statistics_type': 'channel_statistics'}
            ]
            
            accounting_data = [
                {
                    'connection_info': {'has_readers': True, 'has_writers': False},
                    'operations': {'get_count': 10, 'put_count': 5, 'browse_count': 2}
                },
                {
                    'connection_info': {'has_readers': False, 'has_writers': True},
                    'operations': {'get_count': 0, 'put_count': 15, 'browse_count': 0}
                }
            ]
            
            summary = reader._generate_summary(stats_data, accounting_data)
            
            assert summary['total_messages'] == 4
            assert summary['readers_identified'] == 1
            assert summary['writers_identified'] == 1
            assert summary['queue_operations']['total_gets'] == 10
            assert summary['queue_operations']['total_puts'] == 20
            assert summary['queue_operations']['total_browses'] == 2
            assert summary['statistics_types']['queue_statistics'] == 1
            assert summary['statistics_types']['channel_statistics'] == 1

    def test_parse_statistics_message_valid(self):
        """Test parsing valid statistics message"""
        with patch.dict(sys.modules, {
            'config': MagicMock(**self.mock_config),
            'pcf_parser': MagicMock()
        }):
            reader = MQStatsReader()
            
            # Mock PCF parser
            mock_pcf_data = {
                'header': {'message_type': 'statistics'},
                'parameters': []
            }
            reader.pcf_parser.parse_message.return_value = mock_pcf_data
            reader.pcf_parser.extract_queue_operations.return_value = {
                'queue_name': 'TEST.QUEUE',
                'get_count': 10
            }
            
            # Mock message descriptor
            mock_md = MagicMock()
            mock_md.MsgId = b'12345678901234567890123456789012'
            mock_md.CorrelId = b'12345678901234567890123456789012'
            mock_md.PutDate = '20251108'
            mock_md.PutTime = '13000000'
            
            message = b'sample_pcf_message'
            result = reader._parse_statistics_message(message, mock_md)
            
            assert result is not None
            assert result['message_type'] == 'statistics'
            assert 'timestamp' in result
            assert 'pcf_data' in result
            assert 'queue_operations' in result

    def test_parse_statistics_message_invalid(self):
        """Test parsing invalid statistics message"""
        with patch.dict(sys.modules, {
            'config': MagicMock(**self.mock_config),
            'pcf_parser': MagicMock()
        }):
            reader = MQStatsReader()
            
            # Mock PCF parser to return None (invalid message)
            reader.pcf_parser.parse_message.return_value = None
            
            mock_md = MagicMock()
            mock_md.MsgId = b'invalid'
            mock_md.CorrelId = b'invalid'
            mock_md.PutDate = '20251108'
            mock_md.PutTime = '13000000'
            
            message = b'invalid_message'
            result = reader._parse_statistics_message(message, mock_md)
            
            assert result is not None
            assert result['message_type'] == 'statistics'
            assert result['pcf_header_parsed'] is False

    @patch('sys.modules')
    def test_reset_statistics_disabled(self, mock_modules):
        """Test statistics reset when disabled"""
        config_with_reset_disabled = {
            **self.mock_config,
            'STATS_CONFIG': {'reset_after_read': False}
        }
        
        mock_modules.__setitem__('config', MagicMock(**config_with_reset_disabled))
        mock_modules.__setitem__('pcf_parser', MagicMock())
        
        reader = MQStatsReader()
        result = reader.reset_statistics()
        
        assert result is True

    def test_identify_statistics_type(self):
        """Test statistics type identification"""
        with patch.dict(sys.modules, {
            'config': MagicMock(**self.mock_config),
            'pcf_parser': MagicMock()
        }):
            reader = MQStatsReader()
            
            # Test queue statistics pattern
            queue_msg = b'test' + b'515441545354495155455545' + b'test'  # Contains "STATSQUEUE" in hex
            result = reader._identify_statistics_type(queue_msg)
            assert result == 'queue_statistics'
            
            # Test unknown pattern
            unknown_msg = b'unknown_pattern'
            result = reader._identify_statistics_type(unknown_msg)
            assert result == 'unknown_statistics'


if __name__ == '__main__':
    pytest.main([__file__])
