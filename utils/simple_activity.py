#!/usr/bin/env python3
"""
Simple IBM MQ Activity Generator

This script generates basic queue activity on system queues to create
statistics and accounting data for testing the MQ statistics reader.
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


def generate_simple_activity(qmgr):
    """Generate activity on application queues"""
    queues = ["APP1.REQ", "APP2.REQ"]
    
    for queue_name in queues:
        print(f"Generating activity on {queue_name}...")
        
        try:
            # Put a few test messages
            put_queue = pymqi.Queue(qmgr, queue_name, pymqi.CMQC.MQOO_OUTPUT)
            
            for i in range(3):
                message = f"Test message {i+1} - {datetime.now().isoformat()}"
                md = pymqi.MD()
                # Note: pymqi attribute access may vary by version
                # Using direct assignment which works for most versions
                put_queue.put(message.encode('utf-8'), md)
                time.sleep(0.5)
                
            put_queue.close()
            print(f"✓ Put 3 messages to {queue_name}")
            
            # Try to browse the messages
            browse_queue = pymqi.Queue(qmgr, queue_name, pymqi.CMQC.MQOO_BROWSE)
            gmo = pymqi.GMO()
            
            browse_count = 0
            try:
                while browse_count < 2:
                    md = pymqi.MD()
                    message = browse_queue.get(None, md, gmo)
                    browse_count += 1
            except pymqi.MQMIError as e:
                if e.reason != pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                    print(f"Browse error: {e}")
            
            browse_queue.close()
            print(f"✓ Browsed {browse_count} messages in {queue_name}")
            
            # Get some messages to create reader activity
            get_queue = pymqi.Queue(qmgr, queue_name, pymqi.CMQC.MQOO_INPUT_AS_Q_DEF)
            gmo = pymqi.GMO()
            
            get_count = 0
            try:
                while get_count < 2:  # Get 2 out of 3 messages
                    md = pymqi.MD()
                    message = get_queue.get(None, md, gmo)
                    get_count += 1
            except pymqi.MQMIError as e:
                if e.reason != pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                    print(f"Get error: {e}")
            
            get_queue.close()
            print(f"✓ Got {get_count} messages from {queue_name}")
            
        except pymqi.MQMIError as e:
            print(f"✗ Error generating activity on {queue_name}: {e}")
            continue
    
    return True


def connect_to_mq():
    """Connect to IBM MQ"""
    try:
        # Note: pymqi connection methods may vary by version
        # Using the most compatible approach for simple connection
        
        qmgr = pymqi.QueueManager(None)
        qmgr.connect(MQ_CONFIG['queue_manager'])
        
        print(f"✓ Connected to Queue Manager: {MQ_CONFIG['queue_manager']}")
        return qmgr
        
    except pymqi.MQMIError as e:
        print(f"✗ Failed to connect to MQ: {e}")
        return None


def main():
    """Main function"""
    print("Simple IBM MQ Activity Generator")
    print("=" * 35)
    
    # Connect to MQ
    qmgr = connect_to_mq()
    if not qmgr:
        print("Failed to connect to MQ. Check your configuration.")
        sys.exit(1)
    
    try:
        # Generate some activity
        generate_simple_activity(qmgr)
        print("\n✅ Activity generation completed!")
        print("Wait a few seconds, then run: python mq_stats_reader.py")
        
    finally:
        try:
            qmgr.disconnect()
            print("✓ Disconnected from Queue Manager")
        except (pymqi.MQMIError, OSError):
            pass


if __name__ == "__main__":
    main()