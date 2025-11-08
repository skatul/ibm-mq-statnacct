# IBM MQ Statistics and Accounting Queue Reader

This Python program reads IBM MQ statistics and accounting data from system queues, identifies queue readers and writers, resets statistics after reading, and outputs the data in JSON format with timestamps for insertion into time series databases.

## Features

- **Statistics Collection**: Reads from `SYSTEM.ADMIN.STATISTICS.QUEUE` to collect queue, channel, and queue manager statistics
- **Accounting Data**: Reads from `SYSTEM.ADMIN.ACCOUNTING.QUEUE` to track connection and operation accounting information
- **Reader/Writer Identification**: Analyzes message data to identify applications that read from or write to queues
- **Statistics Reset**: Optionally resets statistics after reading to ensure fresh data collection
- **JSON Output**: Formats all data in JSON with ISO timestamps suitable for time series databases
- **PCF Message Parsing**: Includes a comprehensive PCF (Programmable Command Format) parser for structured message analysis
- **Logging**: Comprehensive logging with both file and console output
- **Error Handling**: Robust error handling for MQ connection and message processing issues

## Prerequisites

- IBM MQ Client libraries installed
- Python 3.7 or higher
- Access to IBM MQ Queue Manager (MQQM1 in this configuration)
- Appropriate permissions to read statistics and accounting queues

## Project Structure

```
ibm-mq-statnacct/
├── src/                          # Source code
│   ├── mq_stats_reader.py       # Main MQ statistics reader
│   ├── pcf_parser.py            # PCF message parser
│   ├── config.py                # Configuration module
│   └── __init__.py              # Package marker
├── tests/                       # Test suite (pytest)
│   ├── test_config.py           # Configuration tests
│   ├── test_pcf_parser.py       # PCF parser tests
│   ├── test_mq_reader_workable.py # Working MQ tests
│   └── conftest.py              # Test fixtures
├── scripts/                     # Utility scripts
│   ├── sample-stat-creation/    # Activity generation scripts
│   ├── demo_sample_output.py    # Output format demo
│   ├── example_timeseries.py    # Time series integration examples
│   ├── run_mq_reader.bat        # Windows runner
│   └── run_mq_reader.ps1        # PowerShell runner
├── examples/                    # Example and testing scripts
│   └── test_connection.py       # Connection testing
├── sample-outputs/              # Example JSON outputs
├── logs/                        # Log files directory
├── main.py                      # Main CLI entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Configuration

Edit `config.py` to match your IBM MQ environment:

```python
MQ_CONFIG = {
    "queue_manager": "MQQM1",           # Your queue manager name
    "channel": "APP1.SVRCONN",          # Server connection channel
    "connection_name": "localhost(1414)", # MQ host and port
    "user": "",                         # Username if authentication required
    "password": ""                      # Password if authentication required
}
```

## Usage

### Basic Usage

Run the main program using the CLI entry point:

```powershell
# Basic usage with default settings
python main.py

# Specify output file
python main.py --output-file my_stats.json

# Reset statistics after reading
python main.py --reset-stats

# Enable verbose logging
python main.py --verbose

# Format for specific time series database
python main.py --format influxdb
```

### Continuous Monitoring (NEW!)

Run continuous monitoring for regular data collection:

```powershell
# Run continuously with 60-second intervals
python main.py --continuous

# Custom interval and limited cycles
python main.py --continuous --interval 30 --max-cycles 10

# Production monitoring with verbose output
python main.py --continuous --interval 300 --verbose
```

Or run directly from source:

```powershell
python src/mq_stats_reader.py
```

Or use the provided scripts:

```powershell
# PowerShell script
.\scripts\run_mq_reader.ps1

# Batch file
.\scripts\run_mq_reader.bat
```

This will:
1. Connect to the specified queue manager
2. Read all messages from statistics and accounting queues
3. Parse and analyze the data
4. Output results to console and save to a timestamped JSON file
5. Optionally reset statistics (configurable)

### Configuration Options

In `config.py`, you can configure:

- **Connection Parameters**: Queue manager, channel, host, credentials
- **Statistics Collection**: Enable/disable different types of statistics
- **Reset Behavior**: Whether to reset statistics after reading
- **Output Format**: JSON formatting options

### Sample Output

The program outputs structured JSON data like this:

```json
{
  "collection_info": {
    "timestamp": "2025-11-08T10:30:00.000Z",
    "queue_manager": "MQQM1",
    "channel": "APP1.SVRCONN",
    "statistics_count": 5,
    "accounting_count": 3
  },
  "statistics_data": [
    {
      "message_type": "statistics",
      "timestamp": "2025-11-08T10:30:00.000Z",
      "queue_operations": {
        "queue_name": "MY.APPLICATION.QUEUE",
        "get_count": 150,
        "put_count": 200,
        "has_readers": true,
        "has_writers": true
      }
    }
  ],
  "accounting_data": [
    {
      "message_type": "accounting",
      "connection_info": {
        "channel_name": "APP1.SVRCONN",
        "has_readers": true,
        "has_writers": true
      },
      "operations": {
        "get_count": 150,
        "put_count": 200,
        "browse_count": 10
      }
    }
  ],
  "summary": {
    "total_messages": 8,
    "readers_identified": 2,
    "writers_identified": 3,
    "queue_operations": {
      "total_gets": 150,
      "total_puts": 200,
      "total_browses": 10
    }
  }
}
```

## Testing

### Running Tests

The project includes a comprehensive test suite using pytest:

```powershell
# Run all tests
python -m pytest

# Run specific test suites
python -m pytest tests/test_config.py -v          # Configuration tests
python -m pytest tests/test_pcf_parser.py -v     # PCF parser tests
python -m pytest tests/test_mq_reader_workable.py -v  # MQ reader tests

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

### Test Connection

Test your IBM MQ connection:

```powershell
python examples/test_connection.py
```

### Generate Sample Activity

Create test activity in your IBM MQ queues:

```powershell
# Simple activity generation
python scripts/sample-stat-creation/simple_activity.py

# Advanced activity patterns
python scripts/sample-stat-creation/generate_activity.py
```

### Sample Outputs

Check the `sample-outputs/` directory for example JSON files showing the expected output format.

## Time Series Database Integration

The JSON output is designed for easy insertion into time series databases like:

- **InfluxDB**: Use the timestamp field as the time dimension
- **Prometheus**: Convert metrics to Prometheus format
- **Elasticsearch**: Use as time-based indices
- **TimescaleDB**: Insert directly using timestamp fields

Example InfluxDB integration:
```python
# Convert to InfluxDB line protocol
measurement = "mq_statistics"
tags = f"queue_manager={data['collection_info']['queue_manager']}"
fields = f"get_count={queue_ops['get_count']},put_count={queue_ops['put_count']}"
timestamp = data['collection_info']['timestamp']
line = f"{measurement},{tags} {fields} {timestamp}"
```

## Files Description

- **`mq_stats_reader.py`**: Main program with MQ connection and data collection logic
- **`pcf_parser.py`**: PCF message parser for structured analysis of MQ messages
- **`config.py`**: Configuration file with MQ connection parameters and settings
- **`requirements.txt`**: Python package dependencies
- **`README.md`**: This documentation file

## Logging

The program creates detailed logs in:
- **Console**: Real-time progress and status
- **File**: `mq_stats_reader.log` with detailed debug information

## Error Handling

The program handles common issues:
- MQ connection failures
- Queue access permissions
- Message parsing errors
- Network connectivity issues
- Invalid message formats

## Security Considerations

- Store credentials securely (consider environment variables)
- Use appropriate MQ user permissions
- Secure log files containing sensitive information
- Consider encryption for data in transit

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check queue manager name, channel, and network connectivity
2. **Permission Denied**: Ensure user has access to statistics and accounting queues  
3. **No Messages**: Statistics/accounting may not be enabled on the queue manager
4. **Parse Errors**: Some message formats may not be fully supported

### Enable Statistics

To enable statistics collection on IBM MQ:

```
ALTER QMGR STATQ(ON) STATCHL(ON) STATACLS(ON)
ALTER QLOCAL('YOUR.QUEUE') STATQ(ON)
```

### Enable Accounting

To enable accounting:

```  
ALTER QMGR ACCTQ(ON) ACCTCONO(ENABLED) ACCTMQI(ON)
```

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the functionality.