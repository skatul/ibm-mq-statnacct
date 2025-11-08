"""
Test cases for PCF Parser module.
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pcf_parser import PCFParser


class TestPCFParser:
    """Test cases for PCF Parser"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = PCFParser()

    def test_parser_initialization(self):
        """Test PCF parser initialization"""
        assert self.parser is not None
        assert hasattr(self.parser, 'logger')

    def test_parse_empty_message(self):
        """Test parsing empty message"""
        result = self.parser.parse_message(b'')
        assert result is None

    def test_parse_short_message(self):
        """Test parsing message shorter than PCF header"""
        short_message = b'short'
        result = self.parser.parse_message(short_message)
        assert result is None

    def test_parse_valid_pcf_header(self):
        """Test parsing valid PCF header"""
        # Create minimal PCF header (36 bytes)
        header = bytearray(36)
        header[0:4] = (21).to_bytes(4, 'big')  # MQCFT_STATISTICS
        header[4:8] = (36).to_bytes(4, 'big')  # Structure length
        header[8:12] = (1).to_bytes(4, 'big')  # Version
        header[12:16] = (150).to_bytes(4, 'big')  # Command
        header[16:20] = (1).to_bytes(4, 'big')  # Message sequence
        header[20:24] = (0).to_bytes(4, 'big')  # Control
        header[24:28] = (0).to_bytes(4, 'big')  # Completion code
        header[28:32] = (0).to_bytes(4, 'big')  # Reason code
        header[32:36] = (0).to_bytes(4, 'big')  # Parameter count

        result = self.parser.parse_message(bytes(header))
        
        assert result is not None
        assert 'header' in result
        assert 'parameters' in result
        assert result['header']['structure_type'] == 21
        assert result['header']['message_type'] == 'statistics'
        assert result['header']['parameter_count'] == 0
        assert len(result['parameters']) == 0

    def test_parse_pcf_with_parameters(self, sample_pcf_message):
        """Test parsing PCF message with parameters"""
        result = self.parser.parse_message(sample_pcf_message)
        
        assert result is not None
        assert 'header' in result
        assert 'parameters' in result
        assert result['header']['parameter_count'] == 2
        assert len(result['parameters']) == 2

    def test_determine_message_type(self):
        """Test message type determination"""
        # Test statistics type
        stats_type = self.parser._determine_message_type(21)
        assert stats_type == 'statistics'
        
        # Test accounting type  
        acc_type = self.parser._determine_message_type(22)
        assert acc_type == 'accounting'
        
        # Test unknown type
        unknown_type = self.parser._determine_message_type(999)
        assert unknown_type == 'unknown_type_999'

    def test_get_parameter_name(self):
        """Test parameter name lookup"""
        # Test known parameter (using actual ID from parser)
        queue_name = self.parser._get_parameter_name(1001)
        assert queue_name == 'MQCA_Q_NAME'
        
        # Test unknown parameter
        unknown = self.parser._get_parameter_name(99999)
        assert unknown == 'UNKNOWN_PARAM_99999'

    def test_extract_queue_operations_empty(self):
        """Test extracting queue operations from empty message"""
        result = self.parser.extract_queue_operations({})

        assert result['queue_name'] == 'unknown'
        assert result['get_count'] == 0
        assert result['put_count'] == 0
        assert result['browse_count'] == 0
        assert result['open_input_count'] == 0
        assert result['open_output_count'] == 0

    def test_extract_queue_operations_with_data(self):
        """Test extracting queue operations with valid data"""
        parsed_message = {
            'parameters': [
                {'parameter_name': 'MQCA_Q_NAME', 'value': 'TEST.QUEUE'},
                {'parameter_name': 'MQIA_GET_COUNT', 'value': 25},
                {'parameter_name': 'MQIA_PUT_COUNT', 'value': 30},
                {'parameter_name': 'MQIA_BROWSE_COUNT', 'value': 5},
                {'parameter_name': 'MQIA_OPEN_INPUT_COUNT', 'value': 2},
                {'parameter_name': 'MQIA_OPEN_OUTPUT_COUNT', 'value': 1}
            ]
        }
        
        result = self.parser.extract_queue_operations(parsed_message)
        
        assert result['queue_name'] == 'TEST.QUEUE'
        assert result['get_count'] == 25
        assert result['put_count'] == 30
        assert result['browse_count'] == 5
        assert result['open_input_count'] == 2
        assert result['open_output_count'] == 1
        assert result['has_readers'] is True
        assert result['has_writers'] is True

    def test_extract_connection_info_empty(self):
        """Test extracting connection info from empty message"""
        result = self.parser.extract_connection_info({})
        
        assert result['channel_name'] == 'unknown'
        assert result['connection_name'] == 'unknown'
        assert result['application_name'] == 'unknown'
        assert result['connect_count'] == 0

    def test_extract_connection_info_with_data(self):
        """Test extracting connection info with valid data"""
        parsed_message = {
            'parameters': [
                {'parameter_name': 'MQCACH_CHANNEL_NAME', 'value': 'TEST.SVRCONN'},
                {'parameter_name': 'MQCACH_CONNECTION_NAME', 'value': '192.168.1.100'},
                {'parameter_name': 'MQIA_CONNECT_COUNT', 'value': 5},
                {'parameter_name': 'MQIA_DISC_COUNT', 'value': 2}
            ]
        }
        
        result = self.parser.extract_connection_info(parsed_message)
        
        assert result['channel_name'] == 'TEST.SVRCONN'
        assert result['connection_name'] == '192.168.1.100'
        assert result['connect_count'] == 5
        assert result['disconnect_count'] == 2

    def test_parse_integer_parameter(self):
        """Test parsing integer parameter"""
        # Create integer parameter: header + value
        param_bytes = bytearray(12)
        param_bytes[0:4] = (3004).to_bytes(4, 'big')  # Parameter ID
        param_bytes[4:8] = (3).to_bytes(4, 'big')    # Integer type
        param_bytes[8:12] = (42).to_bytes(4, 'big')  # Value
        
        result = self.parser._parse_integer_parameter(bytes(param_bytes))
        
        assert result['value'] == 42
        assert result['total_length'] == 12

    def test_parse_string_parameter(self):
        """Test parsing string parameter"""
        # Create string parameter: header + length + string
        test_string = b'TEST.QUEUE'
        param_bytes = bytearray(12 + len(test_string))
        param_bytes[0:4] = (2016).to_bytes(4, 'big')  # Parameter ID
        param_bytes[4:8] = (4).to_bytes(4, 'big')     # String type
        param_bytes[8:12] = len(test_string).to_bytes(4, 'big')  # String length
        param_bytes[12:12+len(test_string)] = test_string
        
        result = self.parser._parse_string_parameter(bytes(param_bytes))
        
        assert result['value'] == 'TEST.QUEUE'
        assert result['total_length'] == 12 + len(test_string)

    def test_parse_malformed_message(self):
        """Test parsing malformed PCF message"""
        # Create malformed header that's too short (less than 36 bytes)
        malformed = b'too_short'

        result = self.parser.parse_message(malformed)
        assert result is None
if __name__ == '__main__':
    pytest.main([__file__])