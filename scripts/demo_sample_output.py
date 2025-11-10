#!/usr/bin/env python3
"""
IBM MQ Statistics Reader - Demo with Sample Data

This script demonstrates what the output would look like when MQ statistics
and accounting are properly enabled and there is queue activity.
"""

import json
import sys
import os
from datetime import datetime, timezone

# Add parent directory to path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def create_sample_statistics_data():
    """Create sample statistics data as it would appear from MQ"""
    return [
        {
            "message_type": "statistics",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_id": "414d51204d5151524d31202020202020c9e4a96520009b01",
            "correlation_id": "000000000000000000000000000000000000000000000000",
            "put_date": "20251108",
            "put_time": "13030000",
            "message_length": 1024,
            "pcf_data": {
                "header": {
                    "structure_type": 21,
                    "message_type": "statistics",
                    "command": 150,
                    "parameter_count": 12
                },
                "parameters": [
                    {"parameter_name": "MQCA_Q_NAME", "value": "APP1.REQ"},
                    {"parameter_name": "MQIA_GET_COUNT", "value": 25},
                    {"parameter_name": "MQIA_PUT_COUNT", "value": 30}
                ]
            },
            "queue_operations": {
                "queue_name": "APP1.REQ",
                "get_count": 25,
                "put_count": 30,
                "browse_count": 5,
                "open_input_count": 3,
                "open_output_count": 2,
                "enqueue_count": 30,
                "dequeue_count": 25,
                "has_readers": True,
                "has_writers": True
            },
            "statistics_type": "queue_statistics"
        },
        {
            "message_type": "statistics",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_id": "414d51204d5151524d31202020202020c9e4a96520009b02",
            "correlation_id": "000000000000000000000000000000000000000000000000",
            "put_date": "20251108",
            "put_time": "13030100",
            "message_length": 1024,
            "pcf_data": {
                "header": {
                    "structure_type": 21,
                    "message_type": "statistics",
                    "command": 150,
                    "parameter_count": 12
                },
                "parameters": [
                    {"parameter_name": "MQCA_Q_NAME", "value": "APP2.REQ"},
                    {"parameter_name": "MQIA_GET_COUNT", "value": 15},
                    {"parameter_name": "MQIA_PUT_COUNT", "value": 18}
                ]
            },
            "queue_operations": {
                "queue_name": "APP2.REQ",
                "get_count": 15,
                "put_count": 18,
                "browse_count": 2,
                "open_input_count": 2,
                "open_output_count": 1,
                "enqueue_count": 18,
                "dequeue_count": 15,
                "has_readers": True,
                "has_writers": True
            },
            "statistics_type": "queue_statistics"
        }
    ]


def create_sample_accounting_data():
    """Create sample accounting data as it would appear from MQ"""
    return [
        {
            "message_type": "accounting",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_id": "414d51204d5151524d31202020202020c9e4a96520009c01",
            "correlation_id": "000000000000000000000000000000000000000000000000",
            "put_date": "20251108",
            "put_time": "13030000",
            "message_length": 2048,
            "pcf_data": {
                "header": {
                    "structure_type": 22,
                    "message_type": "accounting",
                    "command": 151,
                    "parameter_count": 20
                },
                "parameters": [
                    {"parameter_name": "MQCACH_CONNECTION_NAME", "value": "192.168.1.100"},
                    {"parameter_name": "MQCACH_CHANNEL_NAME", "value": "APP1.SVRCONN"},
                    {"parameter_name": "MQIA_PUT_COUNT", "value": 30},
                    {"parameter_name": "MQIA_GET_COUNT", "value": 25}
                ]
            },
            "queue_operations": {
                "queue_name": "APP1.REQ",
                "get_count": 25,
                "put_count": 30,
                "browse_count": 5,
                "open_input_count": 3,
                "open_output_count": 2,
                "enqueue_count": 30,
                "dequeue_count": 25,
                "has_readers": True,
                "has_writers": True
            },
            "connection_info": {
                "channel_name": "APP1.SVRCONN",
                "connection_name": "192.168.1.100",
                "application_name": "MyMQApplication",
                "user_id": "mquser",
                "connect_count": 1,
                "disconnect_count": 0
            },
            "connection_info_legacy": {
                "has_readers": True,
                "has_writers": True,
                "connection_name": "192.168.1.100",
                "application_name": "MyMQApplication",
                "channel_name": "APP1.SVRCONN"
            },
            "operations": {
                "get_count": 25,
                "put_count": 30,
                "browse_count": 5,
                "inquire_count": 0
            }
        },
        {
            "message_type": "accounting",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_id": "414d51204d5151524d31202020202020c9e4a96520009c02",
            "correlation_id": "000000000000000000000000000000000000000000000000",
            "put_date": "20251108",
            "put_time": "13030100",
            "message_length": 2048,
            "pcf_data": {
                "header": {
                    "structure_type": 22,
                    "message_type": "accounting",
                    "command": 151,
                    "parameter_count": 20
                },
                "parameters": [
                    {"parameter_name": "MQCACH_CONNECTION_NAME", "value": "192.168.1.101"},
                    {"parameter_name": "MQCACH_CHANNEL_NAME", "value": "APP1.SVRCONN"},
                    {"parameter_name": "MQIA_PUT_COUNT", "value": 18},
                    {"parameter_name": "MQIA_GET_COUNT", "value": 15}
                ]
            },
            "queue_operations": {
                "queue_name": "APP2.REQ",
                "get_count": 15,
                "put_count": 18,
                "browse_count": 2,
                "open_input_count": 2,
                "open_output_count": 1,
                "enqueue_count": 18,
                "dequeue_count": 15,
                "has_readers": True,
                "has_writers": True
            },
            "connection_info": {
                "channel_name": "APP1.SVRCONN",
                "connection_name": "192.168.1.101",
                "application_name": "AnotherMQApp",
                "user_id": "mquser",
                "connect_count": 1,
                "disconnect_count": 0
            },
            "connection_info_legacy": {
                "has_readers": True,
                "has_writers": True,
                "connection_name": "192.168.1.101",
                "application_name": "AnotherMQApp",
                "channel_name": "APP1.SVRCONN"
            },
            "operations": {
                "get_count": 15,
                "put_count": 18,
                "browse_count": 2,
                "inquire_count": 0
            }
        }
    ]


def demo_with_sample_data():
    """Demonstrate the output format with sample data"""
    print("IBM MQ Statistics Reader - Demo with Sample Data")
    print("=" * 60)
    
    # Create sample data
    statistics_data = create_sample_statistics_data()
    accounting_data = create_sample_accounting_data()
    
    # Format the sample data as JSON
    sample_output = {
        "collection_info": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "queue_manager": "MQQM1",
            "channel": "APP1.SVRCONN",
            "statistics_count": len(statistics_data),
            "accounting_count": len(accounting_data)
        },
        "statistics_data": statistics_data,
        "accounting_data": accounting_data,
        "summary": {
            "total_messages": len(statistics_data) + len(accounting_data),
            "readers_identified": 2,
            "writers_identified": 3,
            "queue_operations": {
                "total_gets": sum(stat.get("queue_operations", {}).get("get_count", 0) for stat in statistics_data),
                "total_puts": sum(stat.get("queue_operations", {}).get("put_count", 0) for stat in statistics_data)
            }
        }
    }
    
    output = json.dumps(sample_output, indent=2)
    
    print("Sample JSON Output (as would be generated with real MQ statistics):")
    print("=" * 60)
    print(output)
    
    # Save sample output to file
    filename = f"mq_stats_sample_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)
    
    print(f"\nSample data saved to: {filename}")
    
    # Show what would be in a time series database
    print("\n" + "=" * 60)
    print("Time Series Database Integration Example:")
    print("=" * 60)
    
    data = json.loads(output)
    
    print("\n1. Key Metrics for Time Series:")
    print("   - Total queue operations:", data['summary']['queue_operations'])
    print("   - Readers identified:", data['summary']['readers_identified'])
    print("   - Writers identified:", data['summary']['writers_identified'])
    print("   - Collection timestamp:", data['collection_info']['timestamp'])
    
    print("\n2. Per-Queue Statistics:")
    for stat in data['statistics_data']:
        queue_ops = stat.get('queue_operations', {})
        if queue_ops.get('queue_name') != 'unknown':
            print(f"   Queue: {queue_ops['queue_name']}")
            print(f"     - Gets: {queue_ops['get_count']}, Puts: {queue_ops['put_count']}")
            print(f"     - Has readers: {queue_ops['has_readers']}, Has writers: {queue_ops['has_writers']}")
    
    print("\n3. Connection Information:")
    for acc in data['accounting_data']:
        conn_info = acc.get('connection_info', {})
        print(f"   Channel: {conn_info.get('channel_name', 'unknown')}")
        print(f"     - Connection: {conn_info.get('connection_name', 'unknown')}")
        print(f"     - Application: {conn_info.get('application_name', 'unknown')}")
    
    print("\n" + "=" * 60)
    print("To Enable Real MQ Statistics Collection:")
    print("=" * 60)
    print("Run these MQ commands as an MQ administrator:")
    print()
    print("runmqsc MQQM1")
    print("ALTER QMGR STATQ(ON) STATCHL(ON) STATACLS(ON)")
    print("ALTER QMGR ACCTQ(ON) ACCTCONO(ENABLED) ACCTMQI(ON)")
    print("ALTER QLOCAL('APP1.REQ') STATQ(ON)")
    print("ALTER QLOCAL('APP2.REQ') STATQ(ON)")
    print("END")
    print()
    print("Then generate some activity and run: python mq_stats_reader.py")


if __name__ == "__main__":
    demo_with_sample_data()