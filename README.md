# IBM MQ Statistics and Accounting Queue Reader

A Python application that reads IBM MQ statistics and accounting data from system queues, identifies queue readers and writers, and outputs structured JSON data with timestamps for time series database integration.

Based on the IBM MQ Go implementation reference: https://github.com/skatul/ibmmq-go-stat-otel

## Features

- **Statistics Collection**: Reads from `SYSTEM.ADMIN.STATISTICS.QUEUE` and `SYSTEM.ADMIN.ACCOUNTING.QUEUE`
- **Reader/Writer Identification**: Analyzes PCF messages to identify applications accessing queues
- **JSON Output**: Structured JSON format with ISO timestamps for time series databases
- **Continuous Monitoring**: Configurable interval-based data collection
- **Statistics Reset**: Optional statistics reset after reading for fresh data collection
- **PCF Message Parsing**: Comprehensive parser for IBM MQ Programmable Command Format messages
- **Error Handling**: Robust error handling with detailed logging

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

### Continuous Monitoring

Run continuous monitoring for regular data collection:

```powershell
# Run continuously with 60-second intervals
python main.py --continuous

# Custom interval and limited cycles
python main.py --continuous --interval 30 --max-cycles 10
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

Run the test suite using pytest:

```powershell
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

### Test Connection

```powershell
python examples/test_connection.py
```

## Time Series Database Integration

The JSON output is designed for easy integration with time series databases:

- **InfluxDB**: Direct insertion using timestamp fields
- **Prometheus**: Metrics conversion examples provided
- **Elasticsearch**: Time-based document indexing
- **TimescaleDB**: Compatible timestamp format

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

1. **Connection Failed**: Verify queue manager name, channel, and network connectivity
2. **Permission Denied**: Ensure user has access to statistics and accounting queues  
3. **No Messages**: Statistics/accounting may not be enabled on the queue manager

### Enable Statistics Collection

```
runmqsc QMGR_NAME
ALTER QMGR STATQ(ON) STATCHL(ON) STATACLS(ON)
ALTER QMGR ACCTQ(ON) ACCTCONO(ENABLED) ACCTMQI(ON)
END
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.