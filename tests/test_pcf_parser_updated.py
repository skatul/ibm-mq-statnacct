"""
Updated test cases for PCF Parser with corrected constants integration
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pcf_parser import PCFParser


class TestPCFParserUpdated:
    """Updated test cases for PCF Parser with external constants"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = PCFParser()
    
    def test_parser_initialization(self):
        """Test parser initializes correctly"""
        assert self.parser is not None
    
    def test_message_type_determination(self):
        """Test message type determination using external constants"""
        # Import the constants we need
        try:
            from mq_constants import get_message_type, MQCFT_STATISTICS, MQCFT_ACCOUNTING
            
            # Test statistics type
            stats_type = get_message_type(MQCFT_STATISTICS)
            assert stats_type == 'statistics'
            
            # Test accounting type
            acc_type = get_message_type(MQCFT_ACCOUNTING)
            assert acc_type == 'accounting'
            
            # Test unknown type
            unknown_type = get_message_type(999)
            assert unknown_type == 'unknown_type_999'
            
        except ImportError:
            # If constants module isn't available, skip this test
            pytest.skip("mq_constants module not available")
    
    def test_parameter_name_resolution(self):
        """Test parameter name resolution using external constants"""
        try:
            from mq_constants import get_parameter_name, MQCA_Q_NAME, MQCA_APPL_NAME
            
            # Test known parameters
            queue_name = get_parameter_name(MQCA_Q_NAME)
            assert queue_name == 'MQCA_Q_NAME'
            
            app_name = get_parameter_name(MQCA_APPL_NAME)
            assert app_name == 'MQCA_APPL_NAME'
            
            # Test unknown parameter  
            unknown_param = get_parameter_name(99999)
            assert unknown_param.startswith('UNKNOWN_PARAM_99999')
            
        except ImportError:
            pytest.skip("mq_constants module not available")
    
    def test_connection_info_extraction(self):
        """Test connection info extraction with mock data"""
        # Create a mock message structure
        mock_message = {
            'parameters': [
                {
                    'parameter_id': 2024,  # MQCA_APPL_NAME
                    'parameter_name': 'MQCA_APPL_NAME',
                    'value': 'TestApp.exe'
                },
                {
                    'parameter_id': 3502,  # MQCA_CONNECTION_NAME
                    'parameter_name': 'MQCACH_CONNECTION_NAME',
                    'value': '192.168.1.100(45123)'
                },
                {
                    'parameter_id': 3501,  # MQCA_CHANNEL_NAME
                    'parameter_name': 'MQCACH_CHANNEL_NAME',  
                    'value': 'TEST.SVRCONN'
                }
            ]
        }
        
        # Test extraction
        result = self.parser.extract_connection_info(mock_message)
        
        assert result['application_name'] == 'TestApp.exe'
        assert result['connection_name'] == '192.168.1.100(45123)'
        assert result['channel_name'] == 'TEST.SVRCONN'
    
    def test_queue_operations_extraction(self):
        """Test queue operations extraction with mock data"""
        mock_message = {
            'parameters': [
                {
                    'parameter_id': 2016,  # MQCA_Q_NAME
                    'parameter_name': 'MQCA_Q_NAME',
                    'value': 'TEST.QUEUE'
                },
                {
                    'parameter_id': 66,    # MQIA_OPEN_OUTPUT_COUNT
                    'parameter_name': 'MQIA_OPEN_OUTPUT_COUNT',
                    'value': 2
                },
                {
                    'parameter_id': 65,    # MQIA_OPEN_INPUT_COUNT
                    'parameter_name': 'MQIA_OPEN_INPUT_COUNT',
                    'value': 1
                }
            ]
        }
        
        result = self.parser.extract_queue_operations(mock_message)
        
        assert result['queue_name'] == 'TEST.QUEUE'
        assert result['open_output_count'] == 2
        assert result['open_input_count'] == 1
        assert result['has_writers'] == True
        assert result['has_readers'] == True
    
    def test_producer_detection(self):
        """Test producer detection functionality"""
        producer_message = {
            'parameters': [
                {
                    'parameter_id': 2024,  # MQCA_APPL_NAME
                    'parameter_name': 'MQCA_APPL_NAME',
                    'value': 'ProducerApp.jar'
                },
                {
                    'parameter_id': 66,    # MQIA_OPEN_OUTPUT_COUNT
                    'parameter_name': 'MQIA_OPEN_OUTPUT_COUNT',
                    'value': 3
                },
                {
                    'parameter_id': 65,    # MQIA_OPEN_INPUT_COUNT
                    'parameter_name': 'MQIA_OPEN_INPUT_COUNT',
                    'value': 0
                }
            ]
        }
        
        conn_info = self.parser.extract_connection_info(producer_message)
        queue_ops = self.parser.extract_queue_operations(producer_message)
        
        assert conn_info['application_name'] == 'ProducerApp.jar'
        assert queue_ops['has_writers'] == True
        assert queue_ops['has_readers'] == False
    
    def test_consumer_detection(self):
        """Test consumer detection functionality"""
        consumer_message = {
            'parameters': [
                {
                    'parameter_id': 2024,  # MQCA_APPL_NAME
                    'parameter_name': 'MQCA_APPL_NAME',
                    'value': 'ConsumerApp.exe'
                },
                {
                    'parameter_id': 66,    # MQIA_OPEN_OUTPUT_COUNT
                    'parameter_name': 'MQIA_OPEN_OUTPUT_COUNT',
                    'value': 0
                },
                {
                    'parameter_id': 65,    # MQIA_OPEN_INPUT_COUNT
                    'parameter_name': 'MQIA_OPEN_INPUT_COUNT',
                    'value': 2
                }
            ]
        }
        
        conn_info = self.parser.extract_connection_info(consumer_message)
        queue_ops = self.parser.extract_queue_operations(consumer_message)
        
        assert conn_info['application_name'] == 'ConsumerApp.exe'
        assert queue_ops['has_writers'] == False
        assert queue_ops['has_readers'] == True
    
    def test_empty_message_handling(self):
        """Test handling of empty messages"""
        empty_message = {'parameters': []}
        
        conn_info = self.parser.extract_connection_info(empty_message)
        queue_ops = self.parser.extract_queue_operations(empty_message)
        
        # Should return default values
        assert conn_info['application_name'] == 'unknown'
        assert conn_info['connection_name'] == 'unknown'
        assert queue_ops['queue_name'] == 'unknown'
        assert queue_ops['has_writers'] == False
        assert queue_ops['has_readers'] == False


if __name__ == '__main__':
    pytest.main([__file__])