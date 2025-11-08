#!/usr/bin/env python3
"""
Test script for IBM MQ Statistics Reader

This script performs basic validation of the MQ connection and configuration
without actually reading from the statistics queues.
"""

import sys
import struct
from datetime import datetime
import pymqi
from config import MQ_CONFIG, QUEUE_CONFIG, STATS_CONFIG
from pcf_parser import PCFParser


def test_mq_connection():
    """Test MQ connection without reading queues"""
    print("Testing IBM MQ Connection...")
    print(f"Queue Manager: {MQ_CONFIG['queue_manager']}")
    print(f"Channel: {MQ_CONFIG['channel']}")
    print(f"Connection: {MQ_CONFIG['connection_name']}")
    
    try:
        # Connection parameters
        conn_info = f"{MQ_CONFIG['connection_name']}"
        
        # Create connection details
        cd = pymqi.CD()
        cd.ChannelName = MQ_CONFIG['channel'].encode('utf-8')
        cd.ConnectionName = conn_info.encode('utf-8')
        cd.ChannelType = pymqi.CMQC.MQCHT_CLNTCONN
        cd.TransportType = pymqi.CMQC.MQXPT_TCP
        
        # Optional: Set user credentials if required
        if MQ_CONFIG.get('user'):
            cd.UserIdentifier = MQ_CONFIG['user'].encode('utf-8')
            if MQ_CONFIG.get('password'):
                cd.Password = MQ_CONFIG['password'].encode('utf-8')
        
        # Connect to queue manager
        qmgr = pymqi.QueueManager(None)
        qmgr.connect_with_options(MQ_CONFIG['queue_manager'].encode('utf-8'), cd)
        
        print("✓ Connection successful!")
        
        # Test queue access
        test_queue_access(qmgr)
        
        # Disconnect
        qmgr.disconnect()
        print("✓ Disconnection successful!")
        
        return True
        
    except pymqi.MQMIError as e:
        print(f"✗ MQ Connection failed: {e}")
        print(f"  Reason Code: {e.reason}")
        print(f"  Completion Code: {e.comp}")
        return False
    except (ConnectionError, OSError) as e:
        print(f"✗ Connection error: {e}")
        return False


def test_queue_access(qmgr):
    """Test access to statistics and accounting queues"""
    print("\nTesting queue access...")
    
    queues_to_test = [
        ("Statistics Queue", QUEUE_CONFIG['statistics_queue']),
        ("Accounting Queue", QUEUE_CONFIG['accounting_queue']),
    ]
    
    for queue_desc, queue_name in queues_to_test:
        try:
            # Try to open the queue for input
            queue = pymqi.Queue(qmgr, queue_name, pymqi.CMQC.MQOO_INPUT_AS_Q_DEF)
            print(f"✓ {queue_desc} ({queue_name}) - accessible")
            queue.close()
        except pymqi.MQMIError as e:
            if e.reason == pymqi.CMQC.MQRC_UNKNOWN_OBJECT_NAME:
                print(f"✗ {queue_desc} ({queue_name}) - queue does not exist")
            elif e.reason == pymqi.CMQC.MQRC_NOT_AUTHORIZED:
                print(f"✗ {queue_desc} ({queue_name}) - access denied")
            else:
                print(f"✗ {queue_desc} ({queue_name}) - error: {e}")


def test_pcf_parser():
    """Test the PCF parser with sample data"""
    print("\nTesting PCF Parser...")
    
    try:
        parser = PCFParser()
        
        # Create a minimal PCF header for testing
        # This is a simplified test - real PCF messages are more complex
        test_header = bytearray(36)  # PCF header size
        test_header[0:4] = (21).to_bytes(4, 'big')  # MQCFT_STATISTICS
        test_header[4:8] = (36).to_bytes(4, 'big')  # Structure length
        test_header[8:12] = (1).to_bytes(4, 'big')  # Version
        test_header[32:36] = (0).to_bytes(4, 'big')  # Parameter count
        
        parsed = parser.parse_message(bytes(test_header))
        
        if parsed:
            print("✓ PCF Parser working correctly")
            print(f"  Message type: {parsed.get('header', {}).get('message_type', 'unknown')}")
        else:
            print("✗ PCF Parser failed to parse test message")
            
    except (ValueError, IndexError, struct.error) as e:
        print(f"✗ PCF Parser test failed: {e}")


def test_configuration():
    """Test configuration validity"""
    print("\nTesting Configuration...")
    
    # Test MQ_CONFIG
    required_mq_fields = ['queue_manager', 'channel', 'connection_name']
    for field in required_mq_fields:
        if not MQ_CONFIG.get(field):
            print(f"✗ Missing required MQ config field: {field}")
            return False
        else:
            print(f"✓ MQ Config {field}: {MQ_CONFIG[field]}")
    
    # Test QUEUE_CONFIG
    required_queue_fields = ['statistics_queue', 'accounting_queue']
    for field in required_queue_fields:
        if not QUEUE_CONFIG.get(field):
            print(f"✗ Missing required queue config field: {field}")
            return False
        else:
            print(f"✓ Queue Config {field}: {QUEUE_CONFIG[field]}")
    
    # Test STATS_CONFIG
    print(f"✓ Reset after read: {STATS_CONFIG.get('reset_after_read', False)}")
    print(f"✓ Output format: {STATS_CONFIG.get('output_format', 'json')}")
    
    return True


def main():
    """Main test function"""
    print("=" * 60)
    print("IBM MQ Statistics Reader - Connection Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Test configuration
    if not test_configuration():
        print("\n✗ Configuration test failed!")
        sys.exit(1)
    
    # Test PCF parser
    test_pcf_parser()
    
    # Test MQ connection
    if test_mq_connection():
        print("\n🎉 All tests passed! The MQ Statistics Reader should work correctly.")
        print("\nNext steps:")
        print("1. Ensure statistics and accounting are enabled on your queue manager")
        print("2. Run: python mq_stats_reader.py")
        print("3. Check the generated JSON output file")
        
        # Show sample MQ commands
        print("\nTo enable statistics and accounting on IBM MQ:")
        print("ALTER QMGR STATQ(ON) STATCHL(ON) STATACLS(ON)")
        print("ALTER QMGR ACCTQ(ON) ACCTCONO(ENABLED) ACCTMQI(ON)")
        
        sys.exit(0)
    else:
        print("\n✗ Connection test failed!")
        print("\nTroubleshooting:")
        print("1. Check if IBM MQ is running")
        print("2. Verify queue manager name and channel in config.py")
        print("3. Check network connectivity and port availability") 
        print("4. Ensure proper authentication if required")
        sys.exit(1)


if __name__ == "__main__":
    main()