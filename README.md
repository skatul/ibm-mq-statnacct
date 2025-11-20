# IBM MQ Statistics and Accounting Queue Reader

A Python application that reads IBM MQ statistics and accounting data from system queues, identifies queue readers and writers, and outputs structured JSON data with timestamps for time series database integration.

**Latest Update**: Enhanced PCF parser with improved error handling and IBM MQ 9.4.x compliant constants.

Based on the IBM MQ Go implementation reference: https://github.com/skatul/ibmmq-go-stat-otel

## Features

- **Statistics Collection**: Reads from `SYSTEM.ADMIN.STATISTICS.QUEUE` and `SYSTEM.ADMIN.ACCOUNTING.QUEUE`
- **Producer/Consumer Detection**: Identifies applications producing and consuming messages with client IP extraction
- **Application Tagging**: Extracts application names and user identification from PCF messages
- **JSON Output**: Clean, structured JSON format with ISO timestamps for time series databases
- **Continuous Monitoring**: Configurable interval-based data collection
- **Statistics Reset**: Optional statistics reset after reading for fresh data collection
- **Enhanced PCF Parser**: Robust parser with IBM MQ 9.4.x compliant constants and corruption handling
- **Error Handling**: Advanced error handling with graceful corruption detection and filtering

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
│   ├── pcf_parser.py            # Enhanced PCF message parser
│   ├── mq_constants.py          # IBM MQ 9.4.x compliant constants
│   ├── config.py                # Configuration module
│   └── __init__.py              # Package marker
├── tests/                       # Comprehensive test suite (pytest)
│   ├── test_config.py           # Configuration tests
│   ├── test_pcf_parser.py       # PCF parser tests
│   ├── test_mq_stats_reader.py  # MQ reader tests
│   ├── test_comprehensive.py    # End-to-end test scenarios
│   └── conftest.py              # Test fixtures
├── scripts/                     # Utility scripts
│   ├── run_mq_reader.bat        # Windows runner
│   └── run_mq_reader.ps1        # PowerShell runner
├── examples/                    # Example and testing scripts
│   └── test_connection.py       # Connection testing
├── sample-outputs/              # Example JSON outputs
├── main.py                      # Main CLI entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Recent Improvements

### Enhanced PCF Parser (November 2025)
- **IBM MQ 9.4.x Compliance**: Updated all PCF constants to match official IBM MQ 9.4.x documentation
- **Corruption Handling**: Advanced detection and filtering of corrupted PCF binary data
- **Clean Output**: Eliminates hundreds of `UNKNOWN_PARAM` entries from output
- **Constants Architecture**: Externalized 200+ IBM MQ constants to separate module (`mq_constants.py`)
- **Producer/Consumer Detection**: Enhanced logic for identifying message producers and consumers
- **Client IP Extraction**: Improved extraction of client connection information
- **Error Recovery**: Graceful handling of malformed PCF messages without crashes

### Key Fixes
- ✅ **STAT message type**: Now correctly identified as type 21 (was unknown)
- ✅ **ACCOUNTING message type**: Now correctly identified as type 25 (was unknown)
- ✅ **Parameter parsing**: Robust validation prevents corrupt data from cluttering output
- ✅ **Memory efficiency**: Filtered parsing reduces output size and improves performance

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

Run the comprehensive test suite using pytest:

```powershell
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test modules
python -m pytest tests/test_pcf_parser.py -v
python -m pytest tests/test_comprehensive.py -v
```

**Test Suite Status**: 95.7% success rate with comprehensive coverage
- Core functionality: 100% working
- PCF parser tests: All major scenarios covered
- End-to-end integration: Fully validated
- Configuration tests: Complete coverage

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

- **`src/mq_stats_reader.py`**: Main program with MQ connection and data collection logic
- **`src/pcf_parser.py`**: Enhanced PCF message parser with corruption handling and validation
- **`src/mq_constants.py`**: IBM MQ 9.4.x compliant constants (200+ PCF constants)
- **`src/config.py`**: Configuration file with MQ connection parameters and settings
- **`main.py`**: CLI entry point with comprehensive command-line options
- **`requirements.txt`**: Python package dependencies
- **`README.md`**: This documentation file

### Key Modules

**Enhanced PCF Parser (`pcf_parser.py`)**:
- Robust binary PCF message parsing with error recovery
- Detection and filtering of corrupted parameter data
- Support for multiple parameter types (integer, string, byte string, lists)
- Backwards compatibility with dictionary input for testing

**IBM MQ Constants (`mq_constants.py`)**:
- Complete set of IBM MQ 9.4.x PCF constants
- Message type identification functions
- Parameter name lookup utilities
- Channel and connection type mappings

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