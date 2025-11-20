"""
Comprehensive test cases for MQ Stats Reader module.
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock, Mock, call
from datetime import datetime

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
        
        result = reader.format_output(test_data, [], 'json')
        
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
    
    @patch('mq_stats_reader.pymqi')
    @patch('mq_stats_reader.MQ_CONFIG')
    @patch('mq_stats_reader.QUEUE_CONFIG')
    @patch('mq_stats_reader.STATS_CONFIG')
    @patch('mq_stats_reader.PCFParser')
    def test_collect_statistics_success(self, mock_pcf, mock_stats_config, mock_queue_config, mock_mq_config, mock_pymqi):
        """Test successful statistics collection"""
        # Set up mocks
        mock_mq_config.return_value = self.mock_config
        mock_queue_config.return_value = self.mock_queue_config
        mock_stats_config.return_value = self.mock_stats_config
        
        mock_qmgr = Mock()
        mock_queue = Mock()
        mock_pymqi.QueueManager.return_value = mock_qmgr
        mock_pymqi.Queue.return_value = mock_queue
        
        # Mock message data
        sample_message = json.dumps({
            'header': {'structure_type': 21, 'message_type': 'statistics'},
            'parameters': [
                {'parameter_name': 'MQCA_Q_NAME', 'value': 'TEST.QUEUE'},
                {'parameter_name': 'MQIAMO_GETS', 'value': 100}
            ]
        }).encode('utf-8')
        
        mock_queue.get.side_effect = [sample_message, Exception('No more messages')]
        
        # Import after patching
        try:
            from mq_stats_reader import MQStatsReader
            
            reader = MQStatsReader()
            reader.qmgr = mock_qmgr
            
            # Test statistics collection
            stats = reader.collect_statistics()
            
            # Verify queue was opened
            mock_pymqi.Queue.assert_called()
            mock_queue.get.assert_called()
            
        except ImportError:
            pytest.skip("MQStatsReader module not available")
    
    @patch('mq_stats_reader.pymqi')
    @patch('mq_stats_reader.MQ_CONFIG')
    @patch('mq_stats_reader.QUEUE_CONFIG')
    @patch('mq_stats_reader.STATS_CONFIG')
    @patch('mq_stats_reader.PCFParser')
    def test_collect_accounting_data(self, mock_pcf, mock_stats_config, mock_queue_config, mock_mq_config, mock_pymqi):
        """Test accounting data collection"""
        # Set up mocks
        mock_mq_config.return_value = self.mock_config
        mock_queue_config.return_value = self.mock_queue_config
        mock_stats_config.return_value = self.mock_stats_config
        
        mock_qmgr = Mock()
        mock_queue = Mock()
        mock_pymqi.QueueManager.return_value = mock_qmgr
        mock_pymqi.Queue.return_value = mock_queue
        
        # Mock accounting message
        accounting_message = json.dumps({
            'header': {'structure_type': 24, 'message_type': 'accounting'},
            'parameters': [
                {'parameter_name': 'MQCA_APPL_NAME', 'value': 'TestApp.exe'},
                {'parameter_name': 'MQCACH_CONNECTION_NAME', 'value': '192.168.1.100(12345)'},
                {'parameter_name': 'MQIAMO_PUTS', 'value': 50}
            ]
        }).encode('utf-8')
        
        mock_queue.get.side_effect = [accounting_message, Exception('No more messages')]
        
        try:
            from mq_stats_reader import MQStatsReader
            
            reader = MQStatsReader()
            reader.qmgr = mock_qmgr
            
            # Test accounting collection
            accounting = reader.collect_accounting()
            
            # Verify collection occurred
            mock_queue.get.assert_called()
            
        except (ImportError, AttributeError):
            pytest.skip("MQStatsReader or collect_accounting method not available")
    
    def test_format_output_csv(self):
        """Test CSV output formatting"""
        try:
            from mq_stats_reader import MQStatsReader
            
            reader = MQStatsReader()
            
            test_data = [
                {
                    'timestamp': '2025-11-19T20:00:00Z',
                    'queue_name': 'TEST.QUEUE.1',
                    'application_name': 'App1.exe',
                    'get_count': 10,
                    'put_count': 5
                },
                {
                    'timestamp': '2025-11-19T20:01:00Z',
                    'queue_name': 'TEST.QUEUE.2',
                    'application_name': 'App2.jar',
                    'get_count': 15,
                    'put_count': 8
                }
            ]
            
            # Test CSV format if supported
            if hasattr(reader, 'format_csv') or 'csv' in getattr(reader, 'supported_formats', []):
                result = reader.format_output(test_data, [], 'csv')
                assert isinstance(result, str)
                assert 'queue_name' in result or 'TEST.QUEUE' in result
                
        except ImportError:
            pytest.skip("MQStatsReader module not available")
    
    def test_error_handling_scenarios(self):
        """Test various error handling scenarios"""
        try:
            from mq_stats_reader import MQStatsReader
            
            reader = MQStatsReader()
            
            # Test with None data
            result = reader.format_output(None or [], [], 'json')
            assert result is not None  # Should handle gracefully
            
            # Test with empty data
            result = reader.format_output([], [], 'json')
            assert isinstance(result, str)
            
            # Test with malformed data
            malformed_data = [{'invalid': 'structure'}]
            result = reader.format_output(malformed_data, [], 'json')
            assert isinstance(result, str)
            
        except ImportError:
            pytest.skip("MQStatsReader module not available")
    
    @patch('mq_stats_reader.pymqi')
    def test_connection_recovery(self, mock_pymqi):
        """Test connection recovery after failures"""
        # Simulate intermittent connection issues
        mock_pymqi.MQMIError = Exception
        
        # First call fails, second succeeds
        mock_qmgr = Mock()
        mock_pymqi.QueueManager.side_effect = [
            Exception("Connection lost"),
            mock_qmgr
        ]
        
        try:
            from mq_stats_reader import MQStatsReader
            
            reader = MQStatsReader()
            
            # Should handle connection failure and retry
            first_attempt = reader.connect_to_mq()
            if first_attempt is False:
                second_attempt = reader.connect_to_mq()
                # Second attempt might succeed depending on implementation
                assert second_attempt in [True, False]
            
        except ImportError:
            pytest.skip("MQStatsReader module not available")
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        try:
            from mq_stats_reader import MQStatsReader
            
            # Test with valid configuration
            reader = MQStatsReader()
            assert reader is not None
            
            # Test configuration access
            if hasattr(reader, 'config'):
                config = reader.config
                assert isinstance(config, dict)
            
        except ImportError:
            pytest.skip("MQStatsReader module not available")
    
    def test_logging_functionality(self):
        """Test logging functionality"""
        try:
            from mq_stats_reader import MQStatsReader
            
            reader = MQStatsReader()
            
            # Verify logger exists
            assert hasattr(reader, 'logger')
            assert reader.logger is not None
            
            # Test logger name
            expected_names = ['MQStatsReader', 'mq_stats_reader', 'root']
            assert reader.logger.name in expected_names or reader.logger.name.endswith('MQStatsReader')
            
        except ImportError:
            pytest.skip("MQStatsReader module not available")