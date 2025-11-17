#!/usr/bin/env python3
"""
IBM MQ Statistics Reader - Comprehensive Demo

This comprehensive demo script shows:
1. Enhanced PCF parser parameter resolution 
2. Sample MQ statistics and accounting data output
3. Time series database integration examples
4. Before/after comparison of parameter parsing
"""

import json
from datetime import datetime, timezone

# Use relative import - this script is in demos/ directory
import sys
from pathlib import Path

# Add parent and src directories to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))
sys.path.append(str(parent_dir / 'src'))

# Import only the PCF parser, not the full MQ reader package
from pcf_parser import PCFParser


def demo_parameter_resolution():
    """Demonstrate the enhanced parameter resolution"""
    parser = PCFParser()
    
    print("=" * 80)
    print("SECTION 1: Enhanced PCF Parser - Parameter Resolution")
    print("=" * 80)
    
    # Common parameter IDs that were showing as unknown before the enhancement
    previously_unknown_params = [
        (842019381, 'MQIA_ACCOUNTING_CONN_OVERRIDE'),
        (842019382, 'MQIA_ACCOUNTING_INTERVAL'),
        (842019383, 'MQIA_ACTIVITY_RECORDING'),
        (842019390, 'MQIA_STATISTICS_INTERVAL'),
        (842019391, 'MQIA_STATISTICS_MQI'),
        (842019392, 'MQIA_STATISTICS_Q'),
        (167772161, 'MQCA_APPL_NAME'),
        (167772162, 'MQCA_APPL_IDENTITY_DATA'),
        (301989889, 'MQIA_COMMAND_LEVEL'),
        (536870912, 'MQIA_PUT_TIME'),
        (671088640, 'MQIA_PUT_BYTES'),
    ]
    
    print("\nPreviously Unknown Parameters - Now Resolved:")
    print("-" * 80)
    print(f"{'Parameter ID':<15} {'Hex Value':<12} {'Resolved Name':<35} {'Status'}")
    print("-" * 80)
    
    resolved_count = 0
    for param_id, expected_name in previously_unknown_params:
        resolved_name = parser.get_parameter_name(param_id)
        if resolved_name == expected_name:
            status = "✅ RESOLVED"
            resolved_count += 1
        else:
            status = "❌ MISMATCH"
        print(f"{param_id:<15} 0x{param_id:08X}    {resolved_name:<35} {status}")
    
    print("\nResolution Summary:")
    print(f"  Successfully resolved: {resolved_count}/{len(previously_unknown_params)}")
    print(f"  Resolution rate: {(resolved_count/len(previously_unknown_params))*100:.1f}%")
    
    # Show what an unknown parameter looks like now (with hex value)
    print("\nUnknown parameters now include hex values for easier debugging:")
    unknown_param = 999999999
    unknown_name = parser.get_parameter_name(unknown_param)
    print(f"  {unknown_param} -> {unknown_name}")
    

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
                    {"parameter_name": "MQIA_PUT_COUNT", "value": 30},
                    {"parameter_name": "MQIA_STATISTICS_Q", "value": 1},
                    {"parameter_name": "MQIA_STATISTICS_INTERVAL", "value": 300}
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
                    {"parameter_name": "MQIA_PUT_COUNT", "value": 18},
                    {"parameter_name": "MQIA_STATISTICS_Q", "value": 1}
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
                    {"parameter_name": "MQCA_APPL_NAME", "value": "MyMQApplication"},
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
                    {"parameter_name": "MQCA_APPL_NAME", "value": "AnotherMQApp"},
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
            "operations": {
                "get_count": 15,
                "put_count": 18,
                "browse_count": 2,
                "inquire_count": 0
            }
        }
    ]


def demo_enhanced_message_parsing():
    """Demonstrate parsing a mock message with previously unknown parameters"""
    parser = PCFParser()
    
    print(f"\n{'='*80}")
    print("SECTION 2: Enhanced Message Parsing Demonstration")
    print("=" * 80)
    
    # Create a mock message with parameters that were previously unknown
    mock_message = {
        'header': {
            'structure_type': 21,  # MQCFT_STATISTICS
            'message_type': 'statistics',
            'parameter_count': 8
        },
        'parameters': [
            {
                'parameter_id': 2001,
                'parameter_name': parser.get_parameter_name(2001),
                'value': 'APP1.REQ'
            },
            {
                'parameter_id': 51,  # MQIA_PUT_COUNT
                'parameter_name': parser.get_parameter_name(51),
                'value': 150
            },
            {
                'parameter_id': 52,  # MQIA_GET_COUNT 
                'parameter_name': parser.get_parameter_name(52),
                'value': 125
            },
            {
                'parameter_id': 842019392,  # MQIA_STATISTICS_Q (previously unknown)
                'parameter_name': parser.get_parameter_name(842019392),
                'value': 1
            },
            {
                'parameter_id': 842019390,  # MQIA_STATISTICS_INTERVAL (previously unknown)
                'parameter_name': parser.get_parameter_name(842019390),
                'value': 300
            },
            {
                'parameter_id': 167772161,  # MQCA_APPL_NAME (previously unknown)
                'parameter_name': parser.get_parameter_name(167772161),
                'value': 'MyMQApplication'
            },
            {
                'parameter_id': 536870912,  # MQIA_PUT_TIME (previously unknown)
                'parameter_name': parser.get_parameter_name(536870912),
                'value': 1500
            },
            {
                'parameter_id': 671088640,  # MQIA_PUT_BYTES (previously unknown)
                'parameter_name': parser.get_parameter_name(671088640),
                'value': 2048000
            }
        ]
    }
    
    print("Mock MQ Statistics Message Parameter Resolution:")
    print("-" * 80)
    print(f"{'Parameter ID':<15} {'Parameter Name':<35} {'Value':<15} {'Status'}")
    print("-" * 80)
    
    resolved_count = 0
    for param in mock_message['parameters']:
        param_name = param['parameter_name']
        if not param_name.startswith('UNKNOWN_PARAM_'):
            resolved_count += 1
            status = "✅ RESOLVED"
        else:
            status = "❌ UNKNOWN"
        
        print(f"{param['parameter_id']:<15} {param_name:<35} {str(param['value']):<15} {status}")
    
    print("\nMock Message Resolution Summary:")
    total_params = len(mock_message['parameters'])
    print(f"  Total parameters: {total_params}")
    print(f"  Successfully resolved: {resolved_count}")
    print(f"  Still unknown: {total_params - resolved_count}")
    print(f"  Resolution rate: {(resolved_count/total_params)*100:.1f}%")
    
    # Extract queue operations with enhanced parser
    print("\nExtracted Queue Operations (Enhanced Parser):")
    print("-" * 50)
    operations = parser.extract_queue_operations(mock_message)
    for key, value in operations.items():
        if key in ['queue_name', 'get_count', 'put_count', 'has_readers', 'has_writers']:
            print(f"  {key:20} = {value}")


def demo_sample_output():
    """Demonstrate complete sample output generation"""
    print(f"\n{'='*80}")
    print("SECTION 3: Complete Sample MQ Statistics Output")
    print("=" * 80)
    
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
    
    print("\nSample JSON Output (Enhanced with Resolved Parameters):")
    print("-" * 80)
    print(output[:2000] + "\n  ... (truncated for display)" if len(output) > 2000 else output)
    
    # Save sample output to file
    filename = f"mq_stats_comprehensive_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)
    
    print(f"\nComplete sample data saved to: {filename}")
    
    return json.loads(output)


def demo_time_series_integration(data):
    """Demonstrate time series database integration"""
    print(f"\n{'='*80}")
    print("SECTION 4: Time Series Database Integration Examples")
    print("=" * 80)
    
    print("\n1. Key Metrics Summary:")
    print("-" * 40)
    print(f"   Total queue operations: {data['summary']['queue_operations']}")
    print(f"   Readers identified: {data['summary']['readers_identified']}")
    print(f"   Writers identified: {data['summary']['writers_identified']}")
    print(f"   Collection timestamp: {data['collection_info']['timestamp']}")
    
    print("\n2. Per-Queue Statistics:")
    print("-" * 40)
    for stat in data['statistics_data']:
        ops = stat['queue_operations']
        print(f"   Queue: {ops['queue_name']}")
        print(f"     - Gets: {ops['get_count']}, Puts: {ops['put_count']}")
        print(f"     - Has readers: {ops['has_readers']}, Has writers: {ops['has_writers']}")
    
    print("\n3. Connection Information:")
    print("-" * 40)
    for acc in data['accounting_data']:
        conn = acc['connection_info']
        print(f"   Channel: {conn['channel_name']}")
        print(f"     - Connection: {conn['connection_name']}")
        print(f"     - Application: {conn['application_name']}")
    
    print("\n4. InfluxDB Line Protocol Example:")
    print("-" * 40)
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000000000)  # nanoseconds
    for stat in data['statistics_data']:
        ops = stat['queue_operations']
        line = f"mq_queue_stats,queue_manager={data['collection_info']['queue_manager']},queue_name={ops['queue_name']} "
        line += f"get_count={ops['get_count']},put_count={ops['put_count']},browse_count={ops['browse_count']} {timestamp}"
        print(f"   {line}")
    
    print("\n5. Prometheus Metrics Example:")
    print("-" * 40)
    for stat in data['statistics_data']:
        ops = stat['queue_operations']
        print(f'   mq_queue_get_count{{queue_manager="{data["collection_info"]["queue_manager"]}",queue_name="{ops["queue_name"]}"}} {ops["get_count"]}')
        print(f'   mq_queue_put_count{{queue_manager="{data["collection_info"]["queue_manager"]}",queue_name="{ops["queue_name"]}"}} {ops["put_count"]}')


def main():
    """Main demonstration function"""
    print("IBM MQ Statistics Reader - Comprehensive Enhancement Demo")
    print("=" * 80)
    print("This demo shows the enhanced PCF parser capabilities and sample output")
    print("=" * 80)
    
    # Section 1: Parameter Resolution
    demo_parameter_resolution()
    
    # Section 2: Enhanced Message Parsing
    demo_enhanced_message_parsing()
    
    # Section 3: Sample Output Generation
    data = demo_sample_output()
    
    # Section 4: Time Series Integration
    demo_time_series_integration(data)
    
    # Final Summary
    print(f"\n{'='*80}")
    print("ENHANCEMENT SUMMARY")
    print("=" * 80)
    print("✅ Added comprehensive IBM MQ parameter ID mappings (200+ parameters)")
    print("✅ Enhanced queue operations extraction with additional metrics")  
    print("✅ Improved connection info extraction with channel details")
    print("✅ Added hex values to unknown parameters for debugging")
    print("✅ Better error handling for parameter processing")
    print("✅ Unified demo showing complete functionality")
    print()
    print("Benefits:")
    print("• Significantly fewer 'UNKNOWN_PARAM_' entries in MQ statistics output")
    print("• More meaningful parameter names for analysis and debugging")
    print("• Enhanced time series database integration capabilities")
    print("• Better visibility into MQ queue operations and connections")
    print("• Improved troubleshooting with hex parameter ID display")
    
    print(f"\n{'='*80}")
    print("To Enable Real MQ Statistics Collection:")
    print("=" * 80)
    print("Run these MQ commands as an MQ administrator:")
    print()
    print("runmqsc MQQM1")
    print("ALTER QMGR STATQ(ON) STATCHL(ON) STATACLS(ON)")
    print("ALTER QMGR ACCTQ(ON) ACCTCONO(ENABLED) ACCTMQI(ON)")
    print("ALTER QLOCAL('APP1.REQ') STATQ(ON)")
    print("ALTER QLOCAL('APP2.REQ') STATQ(ON)")
    print("END")
    print()
    print("Then generate activity and run: python main.py")


if __name__ == '__main__':
    main()