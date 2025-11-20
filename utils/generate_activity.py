#!/usr/bin/env python3
"""
Generate IBM MQ Activity for Statistics Testing

This script creates some queue activity to generate statistics and accounting data
that can be read by the MQ statistics reader.
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    import pymqi
    from src.config import MQ_CONFIG
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure pymqi is installed and MQ configuration is available")
    sys.exit(1)


def create_test_queue(qmgr, queue_name):
    """Create a test queue if it doesn't exist"""
    try:
        # Try to access the queue first
        test_queue = pymqi.Queue(qmgr, queue_name, pymqi.CMQC.MQOO_INQUIRE)
        test_queue.close()
        print(f"✓ Queue {queue_name} already exists")
        return True
    except pymqi.MQMIError as e:
        if e.reason == pymqi.CMQC.MQRC_UNKNOWN_OBJECT_NAME:
            try:
                # Queue doesn't exist, create it
                pcf = pymqi.PCFExecute(qmgr)
                args = {
                    b'QName': queue_name.encode('utf-8'),
                    b'QType': pymqi.CMQC.MQQT_LOCAL,
                    b'MaxQDepth': 1000,
                    b'MaxMsgLength': 4194304
                }
                pcf.MQCMD_CREATE_Q(args)
                print(f"✓ Created test queue {queue_name}")
                return True
            except pymqi.MQMIError as create_error:
                print(f"✗ Failed to create queue {queue_name}: {create_error}")
                return False
        else:
            print(f"✗ Error accessing queue {queue_name}: {e}")
            return False


def generate_queue_activity(qmgr, queue_name, num_messages=10):
    """Generate some queue activity (puts and gets)"""
    print(f"\nGenerating activity on queue {queue_name}...")
    
    try:
        # Open queue for putting messages
        put_queue = pymqi.Queue(qmgr, queue_name, pymqi.CMQC.MQOO_OUTPUT)
        
        # Put some messages
        for i in range(num_messages):
            message = f"Test message {i+1} - {datetime.now().isoformat()}"
            md = pymqi.MD()
            md.Format = pymqi.CMQC.MQFMT_STRING
            put_queue.put(message.encode('utf-8'), md)
            
        put_queue.close()
        print(f"✓ Put {num_messages} messages to {queue_name}")
        
        # Open queue for getting messages  
        get_queue = pymqi.Queue(qmgr, queue_name, pymqi.CMQC.MQOO_INPUT_AS_Q_DEF)
        
        # Get some messages (not all)
        messages_to_get = num_messages // 2
        gmo = pymqi.GMO()
        gmo.Options = pymqi.CMQC.MQGMO_NO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
        
        for i in range(messages_to_get):
            try:
                md = pymqi.MD()
                message = get_queue.get(None, md, gmo)
                # Just consume the message
            except pymqi.MQMIError as e:
                if e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                    break
                else:
                    raise
        
        get_queue.close()
        print(f"✓ Got {messages_to_get} messages from {queue_name}")
        
        # Browse some remaining messages
        browse_queue = pymqi.Queue(qmgr, queue_name, pymqi.CMQC.MQOO_BROWSE)
        gmo = pymqi.GMO()
        gmo.Options = pymqi.CMQC.MQGMO_NO_WAIT | pymqi.CMQC.MQGMO_BROWSE_FIRST
        
        browse_count = 0
        try:
            while browse_count < 3:  # Browse up to 3 messages
                md = pymqi.MD()
                message = browse_queue.get(None, md, gmo)
                browse_count += 1
                gmo.Options = pymqi.CMQC.MQGMO_NO_WAIT | pymqi.CMQC.MQGMO_BROWSE_NEXT
        except pymqi.MQMIError as e:
            if e.reason != pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                print(f"Browse error: {e}")
        
        browse_queue.close()
        print(f"✓ Browsed {browse_count} messages in {queue_name}")
        
        return True
        
    except pymqi.MQMIError as e:
        print(f"✗ Error generating activity: {e}")
        return False


def connect_to_mq():
    """Connect to IBM MQ"""
    try:
        conn_info = f"{MQ_CONFIG['connection_name']}"
        
        cd = pymqi.CD()
        cd.ChannelName = MQ_CONFIG['channel'].encode('utf-8')
        cd.ConnectionName = conn_info.encode('utf-8')
        cd.ChannelType = pymqi.CMQC.MQCHT_CLNTCONN
        cd.TransportType = pymqi.CMQC.MQXPT_TCP
        
        if MQ_CONFIG.get('user'):
            cd.UserIdentifier = MQ_CONFIG['user'].encode('utf-8')
            if MQ_CONFIG.get('password'):
                cd.Password = MQ_CONFIG['password'].encode('utf-8')
        
        qmgr = pymqi.QueueManager(None)
        qmgr.connect_with_options(MQ_CONFIG['queue_manager'].encode('utf-8'), cd)
        
        print(f"✓ Connected to Queue Manager: {MQ_CONFIG['queue_manager']}")
        return qmgr
        
    except pymqi.MQMIError as e:
        print(f"✗ Failed to connect to MQ: {e}")
        return None


def enable_statistics(qmgr):
    """Enable statistics collection on the queue manager"""
    try:
        pcf = pymqi.PCFExecute(qmgr)
        
        # Enable queue manager statistics
        args = {
            pymqi.CMQC.MQIA_STATISTICS_Q: pymqi.CMQC.MQMON_ON,
            pymqi.CMQC.MQIA_STATISTICS_CHANNEL: pymqi.CMQC.MQMON_ON,
            pymqi.CMQC.MQIA_STATISTICS_AUTO_CLUSSDR: pymqi.CMQC.MQMON_ON
        }
        
        pcf.MQCMD_CHANGE_Q_MGR(args)
        print("✓ Enabled queue manager statistics")
        
        # Enable accounting
        args = {
            pymqi.CMQC.MQIA_ACCOUNTING_Q: pymqi.CMQC.MQMON_ON,
            pymqi.CMQC.MQIA_ACCOUNTING_CONN_OVERRIDE: pymqi.CMQC.MQMON_ENABLED,
            pymqi.CMQC.MQIA_ACCOUNTING_MQI: pymqi.CMQC.MQMON_ON
        }
        
        pcf.MQCMD_CHANGE_Q_MGR(args)
        print("✓ Enabled queue manager accounting")
        
        return True
        
    except pymqi.MQMIError as e:
        print(f"⚠ Could not enable statistics (may already be enabled): {e}")
        return False


def main():
    """Main function to generate MQ activity"""
    print("IBM MQ Activity Generator for Statistics Testing")
    print("=" * 50)
    
    # Connect to MQ
    qmgr = connect_to_mq()
    if not qmgr:
        print("Failed to connect to MQ. Check your configuration.")
        sys.exit(1)
    
    try:
        # Try to enable statistics
        enable_statistics(qmgr)
        
        # Create test queues
        test_queues = ["TEST.STATS.QUEUE1", "TEST.STATS.QUEUE2"]
        
        for queue_name in test_queues:
            if create_test_queue(qmgr, queue_name):
                generate_queue_activity(qmgr, queue_name, 5)
                time.sleep(1)  # Small delay between queues
        
        print("\n✅ Activity generation completed!")
        print("Wait a few seconds for statistics to be collected, then run:")
        print("  python mq_stats_reader.py")
        
    except (ValueError, TypeError, KeyError) as e:
        print(f"✗ Error during activity generation: {e}")
    
    finally:
        try:
            qmgr.disconnect()
            print("✓ Disconnected from Queue Manager")
        except (pymqi.MQMIError, OSError):
            pass


if __name__ == "__main__":
    main()