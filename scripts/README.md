# Scripts Directory

This directory contains utility scripts and tools for the IBM MQ Stats Reader project.

## Scripts

- `example_timeseries.py` - Examples for integrating with time series databases  
- `run_mq_reader.bat` - Windows batch file to run the MQ stats reader
- `run_mq_reader.ps1` - PowerShell script to run the MQ stats reader

## Usage

### Running the Main Program
```bash
# Using PowerShell script
.\scripts\run_mq_reader.ps1

# Using batch file
.\scripts\run_mq_reader.bat

# Direct Python execution
python main.py
```

### Demo and Examples
```bash
# See time series integration examples
python scripts\example_timeseries.py
```

## Note

Demo scripts and activity generators have been moved to other directories:
- **Demos**: See `demos/` directory for comprehensive demonstration scripts
- **Activity Generators**: See `utils/` directory for MQ activity generation tools