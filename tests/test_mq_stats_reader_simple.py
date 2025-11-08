"""
Simplified test cases for MQ Stats Reader module.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestMQStatsReaderSimple:
    """Simplified test class for MQ Stats Reader"""

    def setup_method(self):
        """Set up test fixtures"""
        # Mock configuration
        self.mock_config = {
            'queue_manager': 'TEST_QM',
            'channel': 'TEST.SVRCONN',
            'connection_name': 'localhost(1414)',
            'user': 'testuser',
            'password': 'testpass'
        }

        self.mock_queue_config = {
            'statistics_queue': 'SYSTEM.ADMIN.STATISTICS.QUEUE',
            'accounting_queue': 'SYSTEM.ADMIN.ACCOUNTING.QUEUE'
        }

        self.mock_stats_config = {
            'reset_after_read': False,
            'collect_queue_stats': True,
            'output_format': 'json'
        }

    @patch('mq_stats_reader.pymqi')
    @patch('mq_stats_reader.MQ_CONFIG')
    @patch('mq_stats_reader.QUEUE_CONFIG')
    @patch('mq_stats_reader.STATS_CONFIG')
    @patch('mq_stats_reader.PCFParser')
    def test_reader_initialization(self, mock_pcf, mock_stats_config, mock_queue_config, mock_mq_config, mock_pymqi):
        """Test MQ stats reader initialization"""
        # Set up mocks
        mock_mq_config.return_value = self.mock_config
        mock_queue_config.return_value = self.mock_queue_config
        mock_stats_config.return_value = self.mock_stats_config
        
        # Import after patching
        from mq_stats_reader import MQStatsReader
        
        reader = MQStatsReader()
        assert reader is not None
        assert hasattr(reader, 'qmgr')
        assert hasattr(reader, 'logger')
        assert hasattr(reader, 'pcf_parser')

    @patch('mq_stats_reader.pymqi')
    @patch('mq_stats_reader.MQ_CONFIG')
    @patch('mq_stats_reader.QUEUE_CONFIG')
    @patch('mq_stats_reader.STATS_CONFIG')
    @patch('mq_stats_reader.PCFParser')
    def test_connect_to_mq_success(self, mock_pcf, mock_stats_config, mock_queue_config, mock_mq_config, mock_pymqi):
        """Test successful MQ connection"""
        # Set up mocks
        mock_mq_config.return_value = self.mock_config
        mock_queue_config.return_value = self.mock_queue_config
        mock_stats_config.return_value = self.mock_stats_config
        
        mock_qmgr = Mock()
        mock_pymqi.QueueManager.return_value = mock_qmgr
        
        # Import after patching
        from mq_stats_reader import MQStatsReader
        
        reader = MQStatsReader()
        result = reader.connect_to_mq()
        
        assert result is True
        assert reader.qmgr == mock_qmgr
        mock_pymqi.QueueManager.assert_called_once()

    @patch('mq_stats_reader.pymqi')
    @patch('mq_stats_reader.MQ_CONFIG')
    @patch('mq_stats_reader.QUEUE_CONFIG')
    @patch('mq_stats_reader.STATS_CONFIG')
    @patch('mq_stats_reader.PCFParser')
    def test_connect_to_mq_failure(self, mock_pcf, mock_stats_config, mock_queue_config, mock_mq_config, mock_pymqi):
        """Test MQ connection failure"""
        # Set up mocks
        mock_mq_config.return_value = self.mock_config
        mock_queue_config.return_value = self.mock_queue_config
        mock_stats_config.return_value = self.mock_stats_config
        
        # Mock pymqi exception
        mock_pymqi.MQMIError = Exception
        mock_pymqi.QueueManager.side_effect = Exception("Connection failed")
        
        # Import after patching
        from mq_stats_reader import MQStatsReader
        
        reader = MQStatsReader()
        result = reader.connect_to_mq()
        
        assert result is False
        assert reader.qmgr is None

    @patch('mq_stats_reader.pymqi')
    @patch('mq_stats_reader.MQ_CONFIG')
    @patch('mq_stats_reader.QUEUE_CONFIG')
    @patch('mq_stats_reader.STATS_CONFIG')
    @patch('mq_stats_reader.PCFParser')
    def test_format_output_json(self, mock_pcf, mock_stats_config, mock_queue_config, mock_mq_config, mock_pymqi):
        """Test JSON output formatting"""
        # Set up mocks
        mock_mq_config.return_value = self.mock_config
        mock_queue_config.return_value = self.mock_queue_config
        mock_stats_config.return_value = self.mock_stats_config
        
        # Import after patching
        from mq_stats_reader import MQStatsReader
        
        reader = MQStatsReader()
        
        test_data = [
            {
                'timestamp': '2024-11-08T12:00:00Z',
                'queue_name': 'TEST.QUEUE',
                'get_count': 10,
                'put_count': 5
            }
        ]
        
        result = reader.format_output(test_data, 'json')
        
        assert '"timestamp":' in result
        assert '"queue_name": "TEST.QUEUE"' in result
        assert '"get_count": 10' in result
        assert '"put_count": 5' in result

    def test_pcf_parser_integration(self):
        """Test PCF parser integration"""
        from pcf_parser import PCFParser
        
        parser = PCFParser()
        assert parser is not None
        
        # Test with empty message
        result = parser.parse_message(b'')
        assert result is None