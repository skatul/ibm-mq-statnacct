#!/usr/bin/env python3
"""
Simple IBM MQ Activity Generator

This script generates basic queue activity on system queues to create
statistics and accounting data for testing the MQ statistics reader.
"""

import sys
import os
import time
from datetime import datetime
import pymqi

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from config import MQ_CONFIG


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
                md.Format = pymqi.CMQC.MQFMT_STRING
                put_queue.put(message.encode('utf-8'), md)
                time.sleep(0.5)
                
            put_queue.close()
            print(f"✓ Put 3 messages to {queue_name}")
            
            # Try to browse the messages
            browse_queue = pymqi.Queue(qmgr, queue_name, pymqi.CMQC.MQOO_BROWSE)
            gmo = pymqi.GMO()
            gmo.Options = pymqi.CMQC.MQGMO_NO_WAIT | pymqi.CMQC.MQGMO_BROWSE_FIRST
            
            browse_count = 0
            try:
                while browse_count < 2:
                    md = pymqi.MD()
                    message = browse_queue.get(None, md, gmo)
                    browse_count += 1
                    gmo.Options = pymqi.CMQC.MQGMO_NO_WAIT | pymqi.CMQC.MQGMO_BROWSE_NEXT
            except pymqi.MQMIError as e:
                if e.reason != pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                    print(f"Browse error: {e}")
            
            browse_queue.close()
            print(f"✓ Browsed {browse_count} messages in {queue_name}")
            
            # Get some messages to create reader activity
            get_queue = pymqi.Queue(qmgr, queue_name, pymqi.CMQC.MQOO_INPUT_AS_Q_DEF)
            gmo = pymqi.GMO()
            gmo.Options = pymqi.CMQC.MQGMO_NO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
            
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