# Utils Directory

This directory contains utility scripts for generating IBM MQ activity and supporting the statistics reader.

## Scripts

- `generate_activity.py` - Comprehensive MQ activity generator with queue creation
- `simple_activity.py` - Basic MQ activity generator for existing queues

## Usage

### Generate Comprehensive Activity
```bash
python utils\generate_activity.py
```

This script:
- Creates test queues if they don't exist
- Generates PUT, GET, and BROWSE operations
- Enables statistics and accounting collection
- Provides detailed activity reporting

### Generate Simple Activity  
```bash
python utils\simple_activity.py
```

This script:
- Works with existing APP1.REQ and APP2.REQ queues
- Generates basic PUT/GET/BROWSE activity
- Lighter weight for quick testing
- Minimal queue manager configuration changes

## Prerequisites

Both scripts require:
- IBM MQ client libraries installed
- `pymqi` Python package installed
- MQ configuration in `src/config.py`
- Access to an IBM MQ queue manager

Install pymqi:
```bash
pip install pymqi
```

## MQ Configuration

Ensure your `src/config.py` has proper MQ connection details:

```python
MQ_CONFIG = {
    'queue_manager': 'YOUR_QM_NAME',
    'channel': 'YOUR_CHANNEL', 
    'connection_name': 'localhost(1414)',
    'user': 'mquser',  # Optional
    'password': 'password'  # Optional
}
```

## Generated Activity

Both scripts create activity that will appear in MQ statistics:

### Queue Operations
- **PUT operations**: Messages added to queues
- **GET operations**: Messages retrieved from queues  
- **BROWSE operations**: Messages viewed without removal
- **OPEN operations**: Queue open/close tracking

### Statistics Generated
- Queue depth changes
- Message counts (put/get/browse)
- Application connection tracking
- Channel activity monitoring
- Timing and performance metrics

## Workflow

1. **Configure MQ**: Ensure statistics collection is enabled
2. **Run activity generator**: Use one of the scripts above
3. **Wait briefly**: Allow MQ to collect statistics (30-60 seconds)
4. **Run stats reader**: `python main.py`
5. **Review output**: Enhanced parameter resolution in action

## Troubleshooting

### Connection Issues
- Verify MQ queue manager is running
- Check channel and connection name in config
- Ensure user has proper MQ permissions

### Queue Issues  
- `generate_activity.py` creates queues automatically
- `simple_activity.py` requires existing APP1.REQ and APP2.REQ queues
- Check queue permissions for PUT/GET operations

### Import Errors
- Ensure `pymqi` is installed: `pip install pymqi`
- Verify MQ client libraries are properly installed
- Check Python path includes project src directory

## Note on Import Methods

The scripts use clean relative imports without hardcoded paths:
```python
# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from src.config import MQ_CONFIG
```

This ensures the scripts work regardless of the current working directory.