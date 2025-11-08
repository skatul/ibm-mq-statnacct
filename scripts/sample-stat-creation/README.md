# Sample Statistics Creation Scripts

This directory contains scripts for generating sample IBM MQ activity and statistics for testing the MQ Stats Reader.

## Scripts

- `simple_activity.py` - Creates simple message activity in APP1.REQ and APP2.REQ queues
- `generate_activity.py` - Advanced activity generator with configurable patterns

## Purpose

These scripts are used to:
- Generate test data in IBM MQ queues
- Create realistic message activity patterns
- Test the MQ Stats Reader functionality
- Demonstrate queue reader/writer identification

## Usage

### Simple Activity Generation
```bash
python simple_activity.py
```
This script will:
- Connect to MQQM1 queue manager
- Put messages to APP1.REQ and APP2.REQ
- Create get/put activity for statistics generation

### Advanced Activity Generation
```bash
python generate_activity.py
```
This script provides:
- Configurable message patterns
- Multiple queue activity simulation
- Realistic workload generation

## Requirements

- IBM MQ client libraries (pymqi)
- Access to MQQM1 queue manager
- APP1.SVRCONN channel connection
- APP1.REQ and APP2.REQ queues

## Configuration

Modify the connection parameters in each script if needed:
```python
QUEUE_MANAGER = 'MQQM1'
CHANNEL = 'APP1.SVRCONN'
CONNECTION_NAME = 'localhost(5200)'
QUEUES = ['APP1.REQ', 'APP2.REQ']
```