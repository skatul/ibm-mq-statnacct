"""
Test cases for Configuration module.
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestConfiguration:
    """Test cases for Configuration"""

    def setup_method(self):
        """Set up test fixtures"""
        # Import after adding to path
        try:
            import config
            self.config = config
        except ImportError:
            pytest.skip("Config module not available")

    def test_mq_config_exists(self):
        """Test MQ configuration exists and has required fields"""
        assert hasattr(self.config, 'MQ_CONFIG')
        mq_config = self.config.MQ_CONFIG
        
        required_fields = ['queue_manager', 'channel', 'connection_name']
        for field in required_fields:
            assert field in mq_config, f"Missing required MQ config field: {field}"
            assert mq_config[field], f"MQ config field {field} is empty"

    def test_queue_config_exists(self):
        """Test Queue configuration exists and has required fields"""
        assert hasattr(self.config, 'QUEUE_CONFIG')
        queue_config = self.config.QUEUE_CONFIG
        
        required_fields = ['statistics_queue', 'accounting_queue']
        for field in required_fields:
            assert field in queue_config, f"Missing required queue config field: {field}"
            assert queue_config[field], f"Queue config field {field} is empty"

    def test_stats_config_exists(self):
        """Test Statistics configuration exists and has required fields"""
        assert hasattr(self.config, 'STATS_CONFIG')
        stats_config = self.config.STATS_CONFIG
        
        required_fields = ['output_format', 'include_timestamps']
        for field in required_fields:
            assert field in stats_config, f"Missing required stats config field: {field}"

    def test_mq_config_values(self):
        """Test MQ configuration values are valid"""
        mq_config = self.config.MQ_CONFIG
        
        # Test queue manager name
        assert isinstance(mq_config['queue_manager'], str)
        assert len(mq_config['queue_manager']) > 0
        
        # Test channel name
        assert isinstance(mq_config['channel'], str)
        assert len(mq_config['channel']) > 0
        
        # Test connection name format
        assert isinstance(mq_config['connection_name'], str)
        assert '(' in mq_config['connection_name']  # Should contain port in parentheses

    def test_queue_config_values(self):
        """Test Queue configuration values are valid"""
        queue_config = self.config.QUEUE_CONFIG
        
        # Test statistics queue name
        stats_queue = queue_config['statistics_queue']
        assert isinstance(stats_queue, str)
        assert 'SYSTEM.ADMIN.STATISTICS' in stats_queue
        
        # Test accounting queue name
        acc_queue = queue_config['accounting_queue']
        assert isinstance(acc_queue, str)
        assert 'SYSTEM.ADMIN.ACCOUNTING' in acc_queue

    def test_stats_config_values(self):
        """Test Statistics configuration values are valid"""
        stats_config = self.config.STATS_CONFIG
        
        # Test reset after read flag
        if 'reset_after_read' in stats_config:
            assert isinstance(stats_config['reset_after_read'], bool)
        
        # Test output format
        output_format = stats_config['output_format']
        assert isinstance(output_format, str)
        assert output_format.lower() in ['json', 'xml', 'csv']
        
        # Test include timestamps flag
        include_timestamps = stats_config['include_timestamps']
        assert isinstance(include_timestamps, bool)

    def test_tsdb_config_exists(self):
        """Test Time Series DB configuration exists"""
        assert hasattr(self.config, 'TSDB_CONFIG')
        tsdb_config = self.config.TSDB_CONFIG
        
        assert isinstance(tsdb_config, dict)
        assert 'enabled' in tsdb_config
        assert isinstance(tsdb_config['enabled'], bool)

    def test_config_types(self):
        """Test configuration variable types"""
        # All config objects should be dictionaries
        assert isinstance(self.config.MQ_CONFIG, dict)
        assert isinstance(self.config.QUEUE_CONFIG, dict)
        assert isinstance(self.config.STATS_CONFIG, dict)
        assert isinstance(self.config.TSDB_CONFIG, dict)

    def test_optional_authentication(self):
        """Test optional authentication configuration"""
        mq_config = self.config.MQ_CONFIG
        
        # User and password are optional but should be strings if present
        if 'user' in mq_config:
            assert isinstance(mq_config['user'], str)
        
        if 'password' in mq_config:
            assert isinstance(mq_config['password'], str)

    def test_queue_names_format(self):
        """Test queue names follow IBM MQ naming conventions"""
        queue_config = self.config.QUEUE_CONFIG
        
        for queue_name in queue_config.values():
            if isinstance(queue_name, str):
                # Queue names should not exceed 48 characters (IBM MQ limit)
                assert len(queue_name) <= 48
                # Should not contain invalid characters
                invalid_chars = ['<', '>', '"', '|', '?', '*']
                for char in invalid_chars:
                    assert char not in queue_name

    def test_connection_string_format(self):
        """Test connection string format"""
        connection_name = self.config.MQ_CONFIG['connection_name']
        
        # Should be in format hostname(port) or ip(port)
        assert '(' in connection_name
        assert ')' in connection_name
        
        # Extract and validate port
        port_start = connection_name.rfind('(')
        port_end = connection_name.rfind(')')
        port_str = connection_name[port_start+1:port_end]
        
        # Port should be numeric
        assert port_str.isdigit()
        port = int(port_str)
        assert 1 <= port <= 65535


if __name__ == '__main__':
    pytest.main([__file__])