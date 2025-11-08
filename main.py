#!/usr/bin/env python3
"""
IBM MQ Statistics and Accounting Queue Reader - Main Entry Point

This script serves as the main entry point for the IBM MQ Stats Reader application.
It provides a command-line interface for reading MQ statistics and accounting data.
"""

import sys
import os
import argparse
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def continuous_monitoring(args):
    """Run continuous monitoring with periodic statistics collection"""
    import time
    import signal
    
    print("Starting continuous IBM MQ statistics monitoring...")
    print(f"Collection interval: {args.interval} seconds")
    if args.max_cycles > 0:
        print(f"Maximum cycles: {args.max_cycles}")
    else:
        print("Running indefinitely (Ctrl+C to stop)")
    
    # Set up signal handler for graceful shutdown
    shutdown_requested = False
    
    def signal_handler(signum, frame):
        nonlocal shutdown_requested
        print("\nShutdown requested... finishing current cycle")
        shutdown_requested = True
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    cycle_count = 0
    
    try:
        while not shutdown_requested:
            cycle_count += 1
            print(f"\n{'='*50}")
            print(f"Collection Cycle {cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*50}")
            
            # Perform single collection
            try:
                # Always reset stats in continuous mode for fresh data
                collection_args = args
                collection_args.reset_stats = True
                collection_args._cycle_number = cycle_count
                
                result = single_collection(collection_args)
                
                if result != 0:
                    print(f"Warning: Collection cycle {cycle_count} failed with code {result}")
                else:
                    print(f"✓ Collection cycle {cycle_count} completed successfully")
                
            except Exception as e:
                print(f"Error in collection cycle {cycle_count}: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
            
            # Check if we've reached max cycles
            if args.max_cycles > 0 and cycle_count >= args.max_cycles:
                print(f"\nCompleted {args.max_cycles} collection cycles. Exiting.")
                break
            
            # Wait for next cycle (unless shutdown requested)
            if not shutdown_requested:
                print(f"\nWaiting {args.interval} seconds until next collection...")
                
                # Sleep in small intervals to allow for responsive shutdown
                for _ in range(args.interval):
                    if shutdown_requested:
                        break
                    time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt")
    
    print(f"\nContinuous monitoring stopped after {cycle_count} cycles")
    return 0

def main():
    """Main entry point for the MQ Stats Reader"""
    parser = argparse.ArgumentParser(
        description='IBM MQ Statistics and Accounting Queue Reader',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default settings
  python main.py --output-file stats.json
  python main.py --reset-stats      # Reset statistics after reading
  python main.py --format influxdb # Format for InfluxDB
        """
    )
    
    parser.add_argument(
        '--output-file', '-o',
        help='Output file path (default: mq_stats_<timestamp>.json)',
        default=None
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'influxdb', 'prometheus', 'elasticsearch'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--reset-stats',
        action='store_true',
        help='Reset statistics after reading'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file (overrides default config.py)'
    )
    
    parser.add_argument(
        '--continuous', '-c',
        action='store_true',
        help='Run continuously, collecting stats at regular intervals'
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Interval in seconds for continuous collection (default: 60)'
    )
    
    parser.add_argument(
        '--max-cycles',
        type=int,
        default=0,
        help='Maximum number of collection cycles (0 = unlimited, default: 0)'
    )
    
    args = parser.parse_args()
    
    # Check for continuous mode
    if args.continuous:
        return continuous_monitoring(args)
    else:
        return single_collection(args)

def single_collection(args):
    """Perform a single statistics collection"""
    try:
        # Import after path is set
        from mq_stats_reader import MQStatsReader
        
        # Create reader instance
        reader = MQStatsReader()
        
        # Set verbose logging if requested
        if args.verbose:
            import logging
            logging.basicConfig(level=logging.DEBUG)
        
        # Connect to MQ
        print("Connecting to IBM MQ...")
        if not reader.connect_to_mq():
            print("ERROR: Failed to connect to IBM MQ")
            return 1
        
        print("Successfully connected to MQ")
        
        # Read statistics
        print("Reading statistics and accounting data...")
        statistics_data = reader.read_statistics_queue()
        accounting_data = reader.read_accounting_queue()
        
        if not statistics_data and not accounting_data:
            print("No statistics or accounting data found")
            return 0
        
        print(f"Found {len(statistics_data)} statistics messages, {len(accounting_data)} accounting messages")
        
        # Format output
        output = reader.format_output(statistics_data, accounting_data)
        
        # Determine output file name
        if args.output_file:
            output_file = args.output_file
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # Add cycle number if this is part of continuous monitoring
            if hasattr(args, '_cycle_number'):
                output_file = f"mq_stats_cycle_{args._cycle_number:03d}_{timestamp}.json"
            else:
                output_file = f"mq_stats_{timestamp}.json"
        
        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"Output written to: {output_file}")
        
        # Reset statistics if requested
        if args.reset_stats:
            print("Resetting statistics...")
            reader.reset_statistics()
            print("Statistics reset completed")
        
        # Disconnect
        reader.disconnect_from_mq()
        print("Disconnected from MQ")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())