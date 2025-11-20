# Demos Directory

This directory contains comprehensive demonstration scripts for the IBM MQ Statistics Reader.

## Scripts

- `comprehensive_demo.py` - Complete demo showing all enhanced PCF parser features
- `test_pcf_parser.py` - Test suite for the enhanced PCF parameter resolution

## Usage

### Running the Comprehensive Demo
```bash
python demos\comprehensive_demo.py
```

This demo shows:
- Enhanced PCF parser parameter resolution (200+ parameters)
- Sample MQ statistics and accounting data output  
- Time series database integration examples
- Before/after comparison of parameter parsing

### Testing PCF Parser Enhancements
```bash
python demos\test_pcf_parser.py
```

This test script validates:
- Parameter resolution accuracy across 50+ test cases
- Unknown parameter format with hex values for debugging
- Message parsing with mixed known/unknown parameters
- Overall success rate reporting

## Features Demonstrated

### Parameter Resolution Enhancement
The enhanced PCF parser now resolves 200+ IBM MQ parameter IDs that were previously showing as "unknown_param_xxxxxxxxx". Examples include:

- **Statistics Parameters**: MQIA_STATISTICS_INTERVAL, MQIA_STATISTICS_Q, MQIA_STATISTICS_CHANNEL
- **Accounting Parameters**: MQIA_ACCOUNTING_CONN_OVERRIDE, MQIA_ACCOUNTING_INTERVAL
- **Application Parameters**: MQCA_APPL_NAME, MQCA_APPL_IDENTITY_DATA  
- **Performance Parameters**: MQIA_PUT_TIME, MQIA_PUT_BYTES, MQIA_GET_BYTES
- **Connection Parameters**: MQIA_CONNECTION_COUNT, MQIA_CONNECT_COUNT

### Sample Output Generation
The demos create realistic sample data showing:
- Complete JSON output structure
- Resolved parameter names instead of unknown values
- Queue operations with enhanced metrics
- Connection information with channel details

### Time Series Integration
Examples for integrating with popular time series databases:
- InfluxDB line protocol format
- Prometheus metrics format
- Grafana dashboard ready metrics
- Custom aggregation examples

## Benefits

✅ **Significantly fewer unknown parameters** in MQ statistics output  
✅ **More meaningful parameter names** for analysis and debugging  
✅ **Enhanced time series database integration** capabilities  
✅ **Better visibility** into MQ queue operations and connections  
✅ **Improved troubleshooting** with hex parameter ID display  

## Next Steps

After running the demos:
1. Configure your MQ environment for statistics collection
2. Run the main application: `python main.py`
3. Analyze the enhanced output with resolved parameter names
4. Integrate with your preferred time series database