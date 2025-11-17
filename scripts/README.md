git # Scripts Directory

This directory contains utility scripts and tools for the IBM MQ Stats Reader project.

## Scripts

- `demo_sample_output.py` - Demonstrates expected JSON output format
- `example_timeseries.py` - Examples for integrating with time series databases
- `run_mq_reader.bat` - Windows batch file to run the MQ stats reader
- `run_mq_reader.ps1` - PowerShell script to run the MQ stats reader

## Subdirectories

### sample-stat-creation/
Contains scripts for generating sample statistics and activity in IBM MQ queues for testing purposes.

## Usage

### Running the Main Program
```bash
# Using PowerShell script
.\scripts\run_mq_reader.ps1

# Using batch file
.\scripts\run_mq_reader.bat

# Direct Python execution
python src\mq_stats_reader.py
```

### Generating Test Activity
```bash
# Generate sample activity in APP1.REQ and APP2.REQ
python scripts\sample-stat-creation\simple_activity.py
python scripts\sample-stat-creation\generate_activity.py
```

### Demo and Examples
```bash
# View demo output format
python scripts\demo_sample_output.py

# See time series integration examples
python scripts\example_timeseries.py
```