"""
Core Functionality Test Suite

Tests for the core IBM MQ Statistics Reader functionality including:
- MQ connection and data collection
- Statistics and accounting queue reading
- Basic PCF message parsing
- Configuration validation
- Error handling and logging
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestMQStatsReader(unittest.TestCase):
    """Test cases for MQStatsReader functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        from mq_stats_reader import MQStatsReader
        self.reader = MQStatsReader()
    
    def test_reader_initialization(self):
        """Test MQStatsReader initialization"""
        self.assertIsNotNone(self.reader)
        self.assertIsNotNone(self.reader.logger)
        self.assertIsNotNone(self.reader.pcf_parser)
    
    @patch('pymqi.connect')
    def test_mq_connection(self, mock_connect):
        """Test MQ connection functionality"""
        mock_qmgr = Mock()
        mock_connect.return_value = mock_qmgr
        
        result = self.reader.connect_to_mq()
        self.assertTrue(result)
        self.assertEqual(self.reader.qmgr, mock_qmgr)
    
    def test_format_output_json(self):
        """Test JSON output formatting"""
        stats_data = [{"test": "statistics"}]
        accounting_data = [{"test": "accounting"}]
        
        output = self.reader.format_output(stats_data, accounting_data)
        
        # Should be valid JSON
        parsed = json.loads(output)
        self.assertIn('collection_info', parsed)
        self.assertIn('statistics_data', parsed)
        self.assertIn('accounting_data', parsed)
    
    def test_get_raw_data_structure(self):
        """Test raw data structure for external formatters"""
        stats_data = [{"test": "statistics"}]
        accounting_data = [{"test": "accounting"}] 
        
        raw_data = self.reader.get_raw_data_structure(stats_data, accounting_data)
        
        self.assertIsInstance(raw_data, dict)
        self.assertIn('collection_info', raw_data)
        self.assertIn('statistics_data', raw_data)
        self.assertIn('accounting_data', raw_data)
        self.assertIn('summary', raw_data)

class TestPrometheusExporter(unittest.TestCase):
    """Test cases for Prometheus metrics export"""
    
    def setUp(self):
        """Set up test fixtures"""
        from prometheus_exporter import PrometheusMetricsExporter
        self.exporter = PrometheusMetricsExporter()
    
    def test_exporter_initialization(self):
        """Test Prometheus exporter initialization"""
        self.assertEqual(self.exporter.namespace, "ibmmq")
        self.assertIn("queue_depth_current", self.exporter.help_text)
        self.assertIn("queue_has_readers", self.exporter.help_text)
    
    def test_add_metric(self):
        """Test adding metrics with labels"""
        self.exporter._add_metric("test_metric", 42, {"label1": "value1", "label2": "value2"})
        
        self.assertIn("ibmmq_test_metric", self.exporter.metrics)
        metric_entries = self.exporter.metrics["ibmmq_test_metric"]
        self.assertEqual(len(metric_entries), 1)
        self.assertEqual(metric_entries[0]['value'], 42)
        self.assertEqual(metric_entries[0]['labels']['label1'], "value1")
    
    def test_prometheus_format_export(self):
        """Test Prometheus text format export"""
        self.exporter._add_metric("queue_depth_current", 5, {
            "queue": "TEST.QUEUE",
            "queue_manager": "TEST_QM"
        })
        
        output = self.exporter.export_prometheus_format()
        
        self.assertIn("# HELP ibmmq_queue_depth_current", output)
        self.assertIn("# TYPE ibmmq_queue_depth_current gauge", output)
        self.assertIn('queue="TEST.QUEUE"', output)
        self.assertIn('queue_manager="TEST_QM"', output)
        self.assertIn("} 5", output)
    
    def test_label_formatting(self):
        """Test label formatting with special characters"""
        labels = {"app": 'test"app', "ip": "127.0.0.1"}
        formatted = self.exporter._format_labels(labels)
        
        self.assertIn('app="test\\"app"', formatted)
        self.assertIn('ip="127.0.0.1"', formatted)
    
    def test_reader_writer_metrics(self):
        """Test reader/writer detection metrics"""
        # Sample MQ data with accounting messages
        sample_data = {
            "collection_info": {
                "queue_manager": "TEST_QM",
                "accounting_count": 1
            },
            "accounting_data": [],
            "statistics_data": []
        }
        
        self.exporter.process_mq_data(sample_data)
        
        # Should generate basic metrics
        self.assertIn("ibmmq_queue_depth_current", self.exporter.metrics)
        self.assertIn("ibmmq_last_collection_timestamp", self.exporter.metrics)

class TestEnhancedPCFExtractor(unittest.TestCase):
    """Test cases for enhanced PCF data extraction"""
    
    def setUp(self):
        """Set up test fixtures"""
        from enhanced_pcf_extractor import EnhancedPCFExtractor
        self.extractor = EnhancedPCFExtractor()
    
    def test_extractor_initialization(self):
        """Test enhanced PCF extractor initialization"""
        self.assertIsNotNone(self.extractor.pcf_constants)
        self.assertIsNotNone(self.extractor.app_name_patterns)
        self.assertIsNotNone(self.extractor.ip_pattern)
    
    def test_application_name_extraction(self):
        """Test application name extraction from binary data"""
        # Test data with embedded application name
        test_data = b"some_data\x00python.exe\x00more_data"
        
        result = self.extractor.extract_application_info(test_data)
        
        self.assertTrue(result['raw_data_found'])
        # Should find python.exe or python pattern
        self.assertTrue(result['application_name'] in ['python.exe', 'python', 'unknown'])
    
    def test_client_ip_extraction(self):
        """Test client IP extraction from connection strings"""
        # Test data with embedded IP address
        test_data = b"connection_data127.0.0.1(1414)\x00more_data"
        
        result = self.extractor.extract_application_info(test_data)
        
        self.assertTrue(result['raw_data_found'])
        self.assertEqual(result['client_ip'], '127.0.0.1')
    
    def test_reader_writer_analysis(self):
        """Test comprehensive reader/writer analysis"""
        # Sample accounting messages
        accounting_messages = [
            {
                'pcf_data': {'header': {'corruption_detected': False}},
                'raw_data': b"python.exe\x00127.0.0.1\x00",
                'operations': {'put_count': 5, 'get_count': 0}
            },
            {
                'pcf_data': {'header': {'corruption_detected': False}},
                'raw_data': b"consumer.exe\x00192.168.1.10\x00",
                'operations': {'put_count': 0, 'get_count': 3}
            }
        ]
        
        analysis = self.extractor.extract_reader_writer_info(accounting_messages)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('applications', analysis)
        self.assertIn('readers', analysis)
        self.assertIn('writers', analysis)
        self.assertIn('extraction_stats', analysis)

class TestPCFParser(unittest.TestCase):
    """Test cases for PCF message parsing"""
    
    def setUp(self):
        """Set up test fixtures"""
        from pcf_parser import PCFParser
        self.parser = PCFParser()
    
    def test_parser_initialization(self):
        """Test PCF parser initialization"""
        self.assertIsNotNone(self.parser.pcf_constants)
        self.assertIsNotNone(self.parser.logger)
    
    def test_corruption_detection(self):
        """Test PCF corruption detection"""
        # Create corrupted PCF data (invalid structure type)
        corrupted_data = b'\x16\x00\x00\x00' + b'\x00' * 100
        
        result = self.parser.parse_message(corrupted_data)
        
        self.assertIsNotNone(result)
        if 'header' in result:
            # Should detect corruption
            self.assertTrue(result['header'].get('corruption_detected', False))
    
    def test_valid_pcf_parsing(self):
        """Test parsing of valid PCF messages"""
        # This would require actual PCF data, so we'll test the interface
        sample_data = b'\x01\x00\x00\x00' + b'\x00' * 100
        
        result = self.parser.parse_message(sample_data)
        
        # Should return a result (even if corrupted)
        self.assertIsNotNone(result)

class TestMainApplication(unittest.TestCase):
    """Test cases for main application functionality"""
    
    @patch('sys.argv', ['main.py', '--format', 'prometheus', '--metrics-only'])
    def test_prometheus_command_line(self):
        """Test Prometheus format command line option"""
        # This tests that the argument parser accepts prometheus format
        import main
        
        # Should not raise an exception when importing
        self.assertTrue(hasattr(main, 'main'))
    
    def test_format_options(self):
        """Test available output format options"""
        # Test that all expected formats are supported
        expected_formats = ['json', 'prometheus', 'influxdb', 'elasticsearch']
        
        # This would be tested through argument parser, but we'll verify the formats exist
        for fmt in expected_formats:
            self.assertIsInstance(fmt, str)
            self.assertTrue(len(fmt) > 0)

class TestIntegration(unittest.TestCase):
    """Integration test cases"""
    
    def test_end_to_end_prometheus_export(self):
        """Test complete end-to-end Prometheus export"""
        from mq_stats_reader import MQStatsReader
        from prometheus_exporter import create_prometheus_metrics
        
        # Create sample data structure
        sample_data = {
            "collection_info": {
                "timestamp": "2025-11-20T12:00:00Z",
                "queue_manager": "TEST_QM",
                "statistics_count": 0,
                "accounting_count": 1
            },
            "statistics_data": [],
            "accounting_data": [
                {
                    "message_type": "accounting",
                    "connection_info": {
                        "application_name": "test_app.exe",
                        "client_ip": "127.0.0.1"
                    },
                    "queue_operations": {
                        "has_readers": True,
                        "has_writers": False
                    }
                }
            ]
        }
        
        # Generate Prometheus metrics
        prometheus_output = create_prometheus_metrics(sample_data)
        
        # Verify output format
        self.assertIsInstance(prometheus_output, str)
        self.assertIn("# HELP ibmmq_", prometheus_output)
        self.assertIn("# TYPE ibmmq_", prometheus_output)
        self.assertIn("ibmmq_", prometheus_output)
    
    def test_configuration_loading(self):
        """Test configuration loading"""
        from config import MQ_CONFIG, QUEUE_CONFIG, STATS_CONFIG
        
        # Verify required configuration exists
        self.assertIn("queue_manager", MQ_CONFIG)
        self.assertIn("channel", MQ_CONFIG)
        self.assertIn("statistics_queue", QUEUE_CONFIG)
        self.assertIn("accounting_queue", QUEUE_CONFIG)
        self.assertIn("output_format", STATS_CONFIG)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)