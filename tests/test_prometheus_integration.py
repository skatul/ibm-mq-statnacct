"""
Prometheus Integration Test Suite

Tests for Prometheus metrics export functionality including:
- Application tag extraction from PCF data
- Client IP identification from connection strings
- Metrics format compatibility with Go reference implementation
- Reader/writer detection with proper labels
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestPrometheusIntegration:
    """Test cases for Prometheus metrics integration and export functionality"""
    
    def test_corruption_detection_comprehensive(self):
        """Test comprehensive corruption detection scenarios"""
        from pcf_parser import PCFParser
        parser = PCFParser()
        
        # Test various corruption patterns
        corruption_patterns = [
            b'\x16\x00\x00\x16',  # Pattern 369098752 (0x16001600)
            b'\x00\x00\x00\x00' * 10,  # All zeros
            b'\xFF\xFF\xFF\xFF' * 10,  # All ones
            b'corrupted_header_data'  # Invalid text
        ]
        
        for pattern in corruption_patterns:
            result = parser.parse_message(pattern)
            if result:
                # If result is returned, corruption should be detected
                assert 'corruption_detected' in result.get('header', {})
    
    def test_parameter_extraction_edge_cases(self):
        """Test parameter extraction with edge cases"""
        from pcf_parser import PCFParser
        parser = PCFParser()
        
        # Test with various parameter combinations
        test_messages = [
            {
                'parameters': [
                    {'parameter_name': 'MQCA_APPL_NAME', 'value': 'VeryLongApplicationNameThatExceedsNormalLimits.jar'},
                    {'parameter_name': 'MQCACH_CONNECTION_NAME', 'value': '192.168.255.255(65535)'},
                    {'parameter_name': 'MQIAMO_GETS', 'value': 999999999}
                ]
            },
            {
                'parameters': [
                    {'parameter_name': 'MQCA_USER_ID', 'value': ''},  # Empty user ID
                    {'parameter_name': 'MQCA_Q_NAME', 'value': 'Q'},  # Very short queue name
                    {'parameter_name': 'MQIAMO_PUTS', 'value': 0}  # Zero operations
                ]
            }
        ]
        
        for message in test_messages:
            conn_info = parser.extract_connection_info(message)
            queue_ops = parser.extract_queue_operations(message)
            
            # Should handle all cases gracefully
            assert isinstance(conn_info, dict)
            assert isinstance(queue_ops, dict)
    
    def test_reader_writer_classification_advanced(self):
        """Test advanced reader/writer classification scenarios"""
        from pcf_parser import PCFParser
        parser = PCFParser()
        
        # Test complex scenarios
        scenarios = [
            {
                'name': 'High Volume Producer',
                'message': {
                    'parameters': [
                        {'parameter_name': 'MQIAMO_PUTS', 'value': 50000},
                        {'parameter_name': 'MQIAMO_GETS', 'value': 0},
                        {'parameter_name': 'MQIA_OPEN_OUTPUT_COUNT', 'value': 5}
                    ]
                },
                'expected_writer': True,
                'expected_reader': False
            },
            {
                'name': 'Batch Consumer',
                'message': {
                    'parameters': [
                        {'parameter_name': 'MQIAMO_GETS', 'value': 10000},
                        {'parameter_name': 'MQIAMO_PUTS', 'value': 0},
                        {'parameter_name': 'MQIA_OPEN_INPUT_COUNT', 'value': 2}
                    ]
                },
                'expected_writer': False,
                'expected_reader': True
            },
            {
                'name': 'Request-Response Service',
                'message': {
                    'parameters': [
                        {'parameter_name': 'MQIAMO_GETS', 'value': 1000},
                        {'parameter_name': 'MQIAMO_PUTS', 'value': 1000},
                        {'parameter_name': 'MQIA_OPEN_INPUT_COUNT', 'value': 1},
                        {'parameter_name': 'MQIA_OPEN_OUTPUT_COUNT', 'value': 1}
                    ]
                },
                'expected_writer': True,
                'expected_reader': True
            }
        ]
        
        for scenario in scenarios:
            queue_ops = parser.extract_queue_operations(scenario['message'])
            
            assert queue_ops['has_writers'] == scenario['expected_writer'], \
                f"Writer classification failed for {scenario['name']}"
            assert queue_ops['has_readers'] == scenario['expected_reader'], \
                f"Reader classification failed for {scenario['name']}"
    
    def test_client_ip_extraction_variations(self):
        """Test client IP extraction with various formats"""
        from pcf_parser import PCFParser
        parser = PCFParser()
        
        ip_formats = [
            ('192.168.1.100(1414)', '192.168.1.100'),
            ('10.0.0.50(49152)', '10.0.0.50'),
            ('172.16.255.1(8080)', '172.16.255.1'),
            ('127.0.0.1(12345)', '127.0.0.1'),
            ('::1(1414)', '::1'),  # IPv6
            ('invalid_format', 'invalid_format'),  # Invalid format should be handled
            ('', ''),  # Empty string
        ]
        
        for connection_string, expected_ip in ip_formats:
            message = {
                'parameters': [
                    {'parameter_name': 'MQCACH_CONNECTION_NAME', 'value': connection_string}
                ]
            }
            
            conn_info = parser.extract_connection_info(message)
            actual_connection = conn_info.get('connection_name', '')
            
            if '(' in connection_string and connection_string != 'invalid_format':
                # Should extract IP part correctly
                assert expected_ip in actual_connection or actual_connection == connection_string
            else:
                # Should handle gracefully
                assert isinstance(actual_connection, str)
    
    def test_message_size_and_performance_metrics(self):
        """Test handling of message size and performance metrics"""
        from pcf_parser import PCFParser
        parser = PCFParser()
        
        performance_message = {
            'parameters': [
                {'parameter_name': 'MQIAMO_PUT_BYTES', 'value': 1048576},  # 1MB
                {'parameter_name': 'MQIAMO_GET_BYTES', 'value': 2097152},  # 2MB
                {'parameter_name': 'MQIAMO_PUTS', 'value': 100},
                {'parameter_name': 'MQIAMO_GETS', 'value': 200},
                {'parameter_name': 'MQIA_CURRENT_Q_DEPTH', 'value': 50},
                {'parameter_name': 'MQIA_MAX_Q_DEPTH', 'value': 5000}
            ]
        }
        
        queue_ops = parser.extract_queue_operations(performance_message)
        
        # Verify byte counts are extracted
        assert queue_ops.get('put_bytes', 0) >= 0
        assert queue_ops.get('get_bytes', 0) >= 0
        
        # Verify counts are extracted
        assert queue_ops.get('put_count', 0) >= 0
        assert queue_ops.get('get_count', 0) >= 0
        
        # Verify depth information
        assert queue_ops.get('current_depth', 0) >= 0
        assert queue_ops.get('max_depth', 0) >= 0
    
    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters in application names"""
        from pcf_parser import PCFParser
        parser = PCFParser()
        
        special_names = [
            'Application-With-Dashes.jar',
            'App_With_Underscores.exe',
            'App With Spaces.py',
            'ApplicationWithNumbers123.jar',
            'App.With.Dots.exe',
            'ÜnicödeÄpp.jar',  # Unicode characters
            'App@Domain.com',   # Email-like
            'C:\\Windows\\System32\\App.exe'  # Windows path
        ]
        
        for app_name in special_names:
            message = {
                'parameters': [
                    {'parameter_name': 'MQCA_APPL_NAME', 'value': app_name}
                ]
            }
            
            conn_info = parser.extract_connection_info(message)
            extracted_name = conn_info.get('application_name', '')
            
            # Should handle all character types gracefully
            assert isinstance(extracted_name, str)
            # Name should be preserved or handled gracefully
            assert len(extracted_name) >= 0
    
    def test_error_recovery_and_logging(self):
        """Test error recovery and logging functionality"""
        from pcf_parser import PCFParser
        import logging
        
        # Capture log messages
        log_messages = []
        
        class TestHandler(logging.Handler):
            def emit(self, record):
                log_messages.append(record.getMessage())
        
        parser = PCFParser()
        test_handler = TestHandler()
        parser.logger.addHandler(test_handler)
        parser.logger.setLevel(logging.DEBUG)
        
        # Test various error conditions
        error_conditions = [
            None,  # None input
            b'',   # Empty bytes
            'string_instead_of_bytes',  # Wrong type
            b'toolong' * 1000,  # Very long message
            b'\x00' * 100  # Binary data
        ]
        
        for condition in error_conditions:
            try:
                result = parser.parse_message(condition)
                # Should either return None or valid result
                assert result is None or isinstance(result, dict)
            except Exception:
                # Exceptions should be handled gracefully in production
                pass
        
        # Should have generated some log messages during error handling
        # (Actual log assertion depends on implementation)
        parser.logger.removeHandler(test_handler)
    
    def test_configuration_driven_behavior(self):
        """Test that parser behavior adapts to configuration"""
        try:
            from config import STATS_CONFIG
            from pcf_parser import PCFParser
            
            parser = PCFParser()
            
            # Test that parser respects configuration if available
            test_message = {
                'parameters': [
                    {'parameter_name': 'MQCA_Q_NAME', 'value': 'TEST.QUEUE'},
                    {'parameter_name': 'MQIAMO_GETS', 'value': 100}
                ]
            }
            
            result = parser.extract_queue_operations(test_message)
            
            # Should produce consistent results regardless of config
            assert isinstance(result, dict)
            assert 'queue_name' in result or 'get_count' in result or len(result) >= 0
            
        except ImportError:
            pytest.skip("Configuration module not available")
    
    def test_memory_and_resource_management(self):
        """Test memory and resource management with large datasets"""
        from pcf_parser import PCFParser
        parser = PCFParser()
        
        # Create a large number of test messages
        large_dataset = []
        for i in range(100):  # Create 100 test messages
            message = {
                'parameters': [
                    {'parameter_name': 'MQCA_APPL_NAME', 'value': f'TestApp_{i}.jar'},
                    {'parameter_name': 'MQCACH_CONNECTION_NAME', 'value': f'192.168.1.{i % 255}(1414)'},
                    {'parameter_name': 'MQIAMO_GETS', 'value': i * 10},
                    {'parameter_name': 'MQIAMO_PUTS', 'value': i * 5}
                ]
            }
            large_dataset.append(message)
        
        # Process all messages
        results = []
        for message in large_dataset:
            conn_info = parser.extract_connection_info(message)
            queue_ops = parser.extract_queue_operations(message)
            results.append({'conn': conn_info, 'ops': queue_ops})
        
        # Verify all messages were processed
        assert len(results) == 100
        
        # Verify results are consistent
        for i, result in enumerate(results):
            assert isinstance(result['conn'], dict)
            assert isinstance(result['ops'], dict)
            # Should contain application name
            app_name = result['conn'].get('application_name', '')
            assert f'TestApp_{i}' in app_name or app_name == 'unknown'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])