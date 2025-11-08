#!/usr/bin/env python3
"""
Example: IBM MQ Statistics to Time Series Database Integration

This example shows how to integrate the MQ statistics reader with different
time series databases for historical data storage and analysis.
"""

import json
from datetime import datetime


def format_for_influxdb(mq_data):
    """Format MQ statistics data for InfluxDB line protocol"""
    if not mq_data:
        return []
    
    lines = []
    collection_info = mq_data.get('collection_info', {})
    qmgr = collection_info.get('queue_manager', 'unknown')
    timestamp_ns = int(datetime.fromisoformat(collection_info.get('timestamp', datetime.now().isoformat()).replace('Z', '+00:00')).timestamp() * 1_000_000_000)
    
    # Process statistics data
    for stat in mq_data.get('statistics_data', []):
        queue_ops = stat.get('queue_operations', {})
        if queue_ops.get('queue_name') != 'unknown':
            tags = f"queue_manager={qmgr},queue_name={queue_ops['queue_name']}"
            fields = [
                f"get_count={queue_ops.get('get_count', 0)}",
                f"put_count={queue_ops.get('put_count', 0)}",
                f"browse_count={queue_ops.get('browse_count', 0)}",
                f"enqueue_count={queue_ops.get('enqueue_count', 0)}",
                f"dequeue_count={queue_ops.get('dequeue_count', 0)}"
            ]
            line = f"mq_queue_stats,{tags} {','.join(fields)} {timestamp_ns}"
            lines.append(line)
    
    # Process accounting data
    for acc in mq_data.get('accounting_data', []):
        conn_info = acc.get('connection_info', {})
        operations = acc.get('operations', {})
        
        if conn_info.get('channel_name') != 'unknown':
            tags = f"queue_manager={qmgr},channel_name={conn_info['channel_name']}"
            fields = [
                f"get_count={operations.get('get_count', 0)}",
                f"put_count={operations.get('put_count', 0)}",
                f"browse_count={operations.get('browse_count', 0)}",
                f"has_readers={1 if conn_info.get('has_readers') else 0}",
                f"has_writers={1 if conn_info.get('has_writers') else 0}"
            ]
            line = f"mq_connection_stats,{tags} {','.join(fields)} {timestamp_ns}"
            lines.append(line)
    
    return lines


def format_for_prometheus(mq_data):
    """Format MQ statistics data for Prometheus metrics"""
    if not mq_data:
        return []
    
    metrics = []
    collection_info = mq_data.get('collection_info', {})
    qmgr = collection_info.get('queue_manager', 'unknown')
    
    # Process statistics data
    for stat in mq_data.get('statistics_data', []):
        queue_ops = stat.get('queue_operations', {})
        if queue_ops.get('queue_name') != 'unknown':
            queue_name = queue_ops['queue_name']
            
            metrics.extend([
                f'mq_queue_get_count{{queue_manager="{qmgr}",queue_name="{queue_name}"}} {queue_ops.get("get_count", 0)}',
                f'mq_queue_put_count{{queue_manager="{qmgr}",queue_name="{queue_name}"}} {queue_ops.get("put_count", 0)}',
                f'mq_queue_browse_count{{queue_manager="{qmgr}",queue_name="{queue_name}"}} {queue_ops.get("browse_count", 0)}',
                f'mq_queue_has_readers{{queue_manager="{qmgr}",queue_name="{queue_name}"}} {1 if queue_ops.get("has_readers") else 0}',
                f'mq_queue_has_writers{{queue_manager="{qmgr}",queue_name="{queue_name}"}} {1 if queue_ops.get("has_writers") else 0}'
            ])
    
    return metrics


def format_for_elasticsearch(mq_data):
    """Format MQ statistics data for Elasticsearch documents"""
    if not mq_data:
        return []
    
    documents = []
    collection_info = mq_data.get('collection_info', {})
    base_timestamp = collection_info.get('timestamp')
    
    # Process statistics data
    for stat in mq_data.get('statistics_data', []):
        queue_ops = stat.get('queue_operations', {})
        if queue_ops.get('queue_name') != 'unknown':
            doc = {
                "@timestamp": base_timestamp,
                "type": "mq_queue_statistics",
                "queue_manager": collection_info.get('queue_manager'),
                "queue_name": queue_ops['queue_name'],
                "metrics": {
                    "get_count": queue_ops.get('get_count', 0),
                    "put_count": queue_ops.get('put_count', 0),
                    "browse_count": queue_ops.get('browse_count', 0),
                    "enqueue_count": queue_ops.get('enqueue_count', 0),
                    "dequeue_count": queue_ops.get('dequeue_count', 0)
                },
                "flags": {
                    "has_readers": queue_ops.get('has_readers', False),
                    "has_writers": queue_ops.get('has_writers', False)
                }
            }
            documents.append(doc)
    
    return documents


def simulate_timeseries_insertion():
    """Simulate collecting MQ data and inserting into time series databases"""
    print("IBM MQ Statistics to Time Series Database Integration Example")
    print("=" * 60)
    
    # Note: This is a simulation - in real usage, you would create MQStatsReader() 
    # and call reader.run() to get actual data
    # For demonstration, we'll use sample data
    sample_data = {
        "collection_info": {
            "timestamp": datetime.now().isoformat() + "Z",
            "queue_manager": "MQQM1",
            "channel": "APP1.SVRCONN",
            "statistics_count": 2,
            "accounting_count": 1
        },
        "statistics_data": [
            {
                "message_type": "statistics",
                "timestamp": datetime.now().isoformat() + "Z",
                "queue_operations": {
                    "queue_name": "MY.APPLICATION.QUEUE",
                    "get_count": 150,
                    "put_count": 200,
                    "browse_count": 10,
                    "enqueue_count": 200,
                    "dequeue_count": 150,
                    "has_readers": True,
                    "has_writers": True
                }
            }
        ],
        "accounting_data": [
            {
                "message_type": "accounting",
                "connection_info": {
                    "channel_name": "APP1.SVRCONN",
                    "has_readers": True,
                    "has_writers": True
                },
                "operations": {
                    "get_count": 150,
                    "put_count": 200,
                    "browse_count": 10
                }
            }
        ],
        "summary": {
            "total_messages": 3,
            "readers_identified": 1,
            "writers_identified": 1,
            "queue_operations": {
                "total_gets": 150,
                "total_puts": 200,
                "total_browses": 10
            }
        }
    }
    
    print("Sample MQ Statistics Data:")
    print(json.dumps(sample_data, indent=2))
    print()
    
    # Format for different time series databases
    print("1. InfluxDB Line Protocol Format:")
    influx_lines = format_for_influxdb(sample_data)
    for line in influx_lines:
        print(f"  {line}")
    print()
    
    print("2. Prometheus Metrics Format:")
    prom_metrics = format_for_prometheus(sample_data)
    for metric in prom_metrics:
        print(f"  {metric}")
    print()
    
    print("3. Elasticsearch Documents Format:")
    es_docs = format_for_elasticsearch(sample_data)
    for doc in es_docs:
        print(f"  {json.dumps(doc, indent=2)}")
    print()
    
    print("Integration Notes:")
    print("- InfluxDB: Use HTTP API or client library to POST line protocol data")
    print("- Prometheus: Expose metrics via HTTP endpoint for scraping")
    print("- Elasticsearch: Use bulk API for efficient document insertion")
    print("- TimescaleDB: Convert to SQL INSERT statements with timestamp columns")


def real_data_collection_example():
    """Example of collecting real MQ data (requires MQ connection)"""
    print("\nReal Data Collection Example:")
    print("To collect real MQ statistics data:")
    print()
    print("1. Ensure IBM MQ is running and accessible")
    print("2. Configure connection parameters in config.py")
    print("3. Enable statistics and accounting on queue manager:")
    print("   ALTER QMGR STATQ(ON) STATCHL(ON) STATACLS(ON)")
    print("   ALTER QMGR ACCTQ(ON) ACCTCONO(ENABLED) ACCTMQI(ON)")
    print()
    print("4. Run the collection:")
    
    code_example = """
    from mq_stats_reader import MQStatsReader
    
    # Create reader instance
    reader = MQStatsReader()
    
    # Collect data
    json_output = reader.run()
    
    if json_output:
        # Parse the JSON
        data = json.loads(json_output)
        
        # Format for your time series database
        influx_lines = format_for_influxdb(data)
        
        # Insert into InfluxDB (example)
        # import influxdb_client
        # client = influxdb_client.InfluxDBClient(url="http://localhost:8086", 
        #                                         token="your-token")
        # write_api = client.write_api()
        # write_api.write(bucket="mq-metrics", record=influx_lines)
    """
    
    print(code_example)


if __name__ == "__main__":
    simulate_timeseries_insertion()
    real_data_collection_example()