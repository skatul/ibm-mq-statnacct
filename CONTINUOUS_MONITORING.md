# Continuous Monitoring Guide

## ✅ **Continuous Monitoring Feature Added!**

The IBM MQ Statistics and Accounting Reader now supports continuous monitoring with automatic statistics reset for collecting fresh data at regular intervals.

## 🚀 **Usage**

### Basic Continuous Monitoring
```bash
# Run continuously with default 60-second intervals
python main.py --continuous

# Custom interval (30 seconds)  
python main.py --continuous --interval 30

# Limited number of cycles (run 10 times then stop)
python main.py --continuous --max-cycles 10

# Combination with verbose output
python main.py --continuous --interval 15 --max-cycles 5 --verbose
```

### Command Line Options
- `--continuous, -c`: Enable continuous monitoring mode
- `--interval, -i`: Collection interval in seconds (default: 60)
- `--max-cycles`: Maximum cycles to run (0 = unlimited, default: 0)
- `--verbose, -v`: Enable detailed logging

## 📊 **What It Does**

### Collection Cycle Process
1. **Connect** to IBM MQ queue manager
2. **Read** statistics and accounting queue data
3. **Parse** PCF messages and extract information
4. **Save** JSON output with cycle number in filename
5. **Reset** statistics (if enabled in configuration)
6. **Disconnect** from IBM MQ
7. **Wait** for specified interval
8. **Repeat** until stopped or max cycles reached

### Output Files
Files are automatically named with cycle numbers:
- `mq_stats_cycle_001_20251108_083545.json`
- `mq_stats_cycle_002_20251108_083555.json`
- `mq_stats_cycle_003_20251108_084605.json`

## ⚙️ **Configuration for Continuous Mode**

### Enable Statistics Reset
For fresh data in each cycle, update `src/config.py`:
```python
STATS_CONFIG = {
    "reset_after_read": True,  # Enable for continuous monitoring
    "collect_queue_stats": True,
    "collect_channel_stats": True,
    "collect_qmgr_stats": True,
    "output_format": "json",
    "include_timestamps": True
}
```

### IBM MQ Statistics Configuration
To collect statistics (not just accounting), configure IBM MQ:
```
# Enable statistics collection
ALTER QMGR STATQ(ON) STATCHL(ON) STATACCT(ON)

# Enable statistics for specific queues
ALTER QLOCAL(APP1.REQ) STATQ(ON)
ALTER QLOCAL(APP2.REQ) STATQ(ON)

# Set statistics intervals (optional)
ALTER QMGR STATINT(60)  # Statistics interval in seconds
```

## 🔄 **Graceful Shutdown**

The continuous monitoring supports graceful shutdown:
- **Ctrl+C**: Stop after completing current cycle
- **SIGTERM**: Graceful shutdown on Unix systems
- **Max Cycles**: Automatic stop after specified number of cycles

## 📈 **Use Cases**

### Production Monitoring
```bash
# Monitor every 5 minutes indefinitely
python main.py --continuous --interval 300

# Daily collection (24 cycles of 1 hour each)
python main.py --continuous --interval 3600 --max-cycles 24
```

### Development/Testing
```bash
# Quick testing with 30-second intervals, 5 cycles
python main.py --continuous --interval 30 --max-cycles 5 --verbose

# Generate sample data every 10 seconds
python main.py --continuous --interval 10 --max-cycles 10
```

### Time Series Database Integration
```bash
# Collect for InfluxDB every 2 minutes
python main.py --continuous --interval 120 --reset-stats

# Prometheus-style collection every minute
python main.py --continuous --interval 60 --format json
```

## 🛠️ **Integration with Process Managers**

### systemd Service (Linux)
```ini
[Unit]
Description=IBM MQ Statistics Collector
After=network.target

[Service]
Type=simple
User=mquser
WorkingDirectory=/opt/ibm-mq-stats
ExecStart=/opt/ibm-mq-stats/.venv/bin/python main.py --continuous --interval 60
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Windows Service
Use `nssm` or similar to run as Windows service:
```cmd
nssm install MQStatsCollector "D:\CPP\ibm-mq-statnacct\.venv\Scripts\python.exe"
nssm set MQStatsCollector Arguments "main.py --continuous --interval 60"
nssm set MQStatsCollector AppDirectory "D:\CPP\ibm-mq-statnacct"
```

### Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py", "--continuous", "--interval", "60"]
```

## 📋 **Example Output**

```
Starting continuous IBM MQ statistics monitoring...
Collection interval: 30 seconds
Maximum cycles: 5

==================================================
Collection Cycle 1 - 2025-11-08 08:35:44
==================================================
Connecting to IBM MQ...
Successfully connected to MQ
Reading statistics and accounting data...
Found 0 statistics messages, 1 accounting messages
Output written to: mq_stats_cycle_001_20251108_083545.json
Resetting statistics...
Statistics reset completed
Disconnected from MQ
✓ Collection cycle 1 completed successfully

Waiting 30 seconds until next collection...

==================================================
Collection Cycle 2 - 2025-11-08 08:36:15
==================================================
...
```

## ✅ **Benefits**

1. **Fresh Data**: Statistics reset ensures each cycle captures new activity
2. **Timestamped Output**: Each file contains collection timestamp
3. **Graceful Operation**: Proper connection handling and cleanup
4. **Flexible Scheduling**: Configurable intervals and cycle limits
5. **Production Ready**: Signal handling and error recovery
6. **Integration Friendly**: Easy to integrate with monitoring systems

The continuous monitoring feature makes the IBM MQ Statistics Reader suitable for production monitoring and time series data collection!