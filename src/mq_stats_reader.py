"""
IBM MQ Statistics and Accounting Queue Reader

This program reads IBM MQ statistics and accounting data, identifies readers and writers,
resets statistics after reading, and outputs data in JSON format with timestamps.
Designed for insertion into time series databases for historical tracking.

Author: GitHub Copilot
Date: November 2025
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import pymqi
try:
    from .config import MQ_CONFIG, QUEUE_CONFIG, STATS_CONFIG
    from .pcf_parser import PCFParser
except ImportError:
    # For direct execution or when not imported as a package
    from config import MQ_CONFIG, QUEUE_CONFIG, STATS_CONFIG
    from pcf_parser import PCFParser


class MQStatsReader:
    """Main class for reading IBM MQ statistics and accounting data"""
    
    def __init__(self):
        self.qmgr = None
        self.logger = self._setup_logging()
        self.pcf_parser = PCFParser()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mq_stats_reader.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def connect_to_mq(self) -> bool:
        """Establish connection to IBM MQ Queue Manager"""
        try:
            # Connection parameters
            conn_info = f"{MQ_CONFIG['connection_name']}"
            
            # Create connection details
            cd = pymqi.CD()
            cd.ChannelName = MQ_CONFIG['channel'].encode('utf-8')
            cd.ConnectionName = conn_info.encode('utf-8')
            cd.ChannelType = pymqi.CMQC.MQCHT_CLNTCONN
            cd.TransportType = pymqi.CMQC.MQXPT_TCP
            
            # Optional: Set user credentials if required
            if MQ_CONFIG.get('user'):
                cd.UserIdentifier = MQ_CONFIG['user'].encode('utf-8')
                if MQ_CONFIG.get('password'):
                    cd.Password = MQ_CONFIG['password'].encode('utf-8')
            
            # Connect to queue manager
            self.qmgr = pymqi.QueueManager(None)
            self.qmgr.connect_with_options(MQ_CONFIG['queue_manager'].encode('utf-8'), cd)
            
            self.logger.info("Successfully connected to Queue Manager: %s", MQ_CONFIG['queue_manager'])
            return True
            
        except pymqi.MQMIError as e:
            self.logger.error("Failed to connect to MQ: %s", e)
            return False
        except (ConnectionError, OSError) as e:
            self.logger.error("Connection error during MQ connection: %s", e)
            return False
    
    def disconnect_from_mq(self):
        """Disconnect from IBM MQ Queue Manager"""
        try:
            if self.qmgr:
                self.qmgr.disconnect()
                self.logger.info("Disconnected from Queue Manager")
        except pymqi.MQMIError as e:
            self.logger.error("Error during disconnect: %s", e)
    
    def read_statistics_queue(self) -> List[Dict[str, Any]]:
        """Read messages from the statistics queue"""
        statistics_data = []
        
        try:
            # Open statistics queue for reading
            queue = pymqi.Queue(self.qmgr, QUEUE_CONFIG['statistics_queue'])
            
            # Message descriptor
            md = pymqi.MD()
            
            # Get message options
            gmo = pymqi.GMO()
            gmo.Options = pymqi.CMQC.MQGMO_NO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
            
            message_count = 0
            while True:
                try:
                    # Reset message descriptor for each message
                    md = pymqi.MD()
                    
                    # Get message
                    message = queue.get(None, md, gmo)
                    message_count += 1
                    
                    # Parse the message
                    parsed_data = self._parse_statistics_message(message, md)
                    if parsed_data:
                        statistics_data.append(parsed_data)
                        
                except pymqi.MQMIError as e:
                    if e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                        break  # No more messages
                    else:
                        self.logger.error("Error reading statistics message: %s", e)
                        break
            
            queue.close()
            self.logger.info("Read %d statistics messages", message_count)
            
        except pymqi.MQMIError as e:
            self.logger.error("Failed to read statistics queue: %s", e)
        except (ValueError, TypeError) as e:
            self.logger.error("Data parsing error reading statistics: %s", e)
        
        return statistics_data
    
    def read_accounting_queue(self) -> List[Dict[str, Any]]:
        """Read messages from the accounting queue"""
        accounting_data = []
        
        try:
            # Open accounting queue for reading
            queue = pymqi.Queue(self.qmgr, QUEUE_CONFIG['accounting_queue'])
            
            # Message descriptor
            md = pymqi.MD()
            
            # Get message options
            gmo = pymqi.GMO()
            gmo.Options = pymqi.CMQC.MQGMO_NO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
            
            message_count = 0
            while True:
                try:
                    # Reset message descriptor for each message
                    md = pymqi.MD()
                    
                    # Get message
                    message = queue.get(None, md, gmo)
                    message_count += 1
                    
                    # Parse the message
                    parsed_data = self._parse_accounting_message(message, md)
                    if parsed_data:
                        accounting_data.append(parsed_data)
                        
                except pymqi.MQMIError as e:
                    if e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                        break  # No more messages
                    else:
                        self.logger.error("Error reading accounting message: %s", e)
                        break
            
            queue.close()
            self.logger.info("Read %d accounting messages", message_count)
            
        except pymqi.MQMIError as e:
            self.logger.error("Failed to read accounting queue: %s", e)
        except (ValueError, TypeError) as e:
            self.logger.error("Data parsing error reading accounting: %s", e)
        
        return accounting_data
    
    def _parse_statistics_message(self, message: bytes, md: pymqi.MD) -> Optional[Dict[str, Any]]:
        """Parse a statistics message and extract relevant information"""
        try:
            # Get current timestamp
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Basic message info
            parsed_data = {
                "message_type": "statistics",
                "timestamp": timestamp,
                "message_id": md.MsgId.hex(),
                "correlation_id": md.CorrelId.hex(),
                "put_date": md.PutDate.decode('utf-8') if isinstance(md.PutDate, bytes) else str(md.PutDate),
                "put_time": md.PutTime.decode('utf-8') if isinstance(md.PutTime, bytes) else str(md.PutTime),
                "message_length": len(message)
            }
            
            # Parse PCF message using the dedicated parser
            pcf_data = self.pcf_parser.parse_message(message)
            if pcf_data:
                parsed_data["pcf_data"] = pcf_data
                parsed_data["statistics_type"] = pcf_data.get('header', {}).get('message_type', 'unknown')
                
                # Extract queue operations if this is a queue statistics message
                queue_ops = self.pcf_parser.extract_queue_operations(pcf_data)
                if queue_ops.get('queue_name') != 'unknown':
                    parsed_data["queue_operations"] = queue_ops
            else:
                # Fallback to basic parsing
                parsed_data.update({
                    "pcf_header_parsed": False,
                    "raw_message_preview": message[:100].hex(),
                    "statistics_type": self._identify_statistics_type(message)
                })
                
            return parsed_data
            
        except (ValueError, IndexError, KeyError) as e:
            self.logger.error("Error parsing statistics message: %s", e)
            return None
    
    def _parse_accounting_message(self, message: bytes, md: pymqi.MD) -> Optional[Dict[str, Any]]:
        """Parse an accounting message and extract relevant information"""
        try:
            # Get current timestamp
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Basic message info
            parsed_data = {
                "message_type": "accounting",
                "timestamp": timestamp,
                "message_id": md.MsgId.hex(),
                "correlation_id": md.CorrelId.hex(),
                "put_date": md.PutDate.decode('utf-8') if isinstance(md.PutDate, bytes) else str(md.PutDate),
                "put_time": md.PutTime.decode('utf-8') if isinstance(md.PutTime, bytes) else str(md.PutTime),
                "message_length": len(message)
            }
            
            # Parse PCF message using the dedicated parser
            pcf_data = self.pcf_parser.parse_message(message)
            if pcf_data:
                parsed_data["pcf_data"] = pcf_data
                
                # Extract queue operations and connection info
                queue_ops = self.pcf_parser.extract_queue_operations(pcf_data)
                conn_info = self.pcf_parser.extract_connection_info(pcf_data)
                
                parsed_data["queue_operations"] = queue_ops
                parsed_data["connection_info"] = conn_info
                
                # Legacy format for compatibility
                parsed_data["connection_info_legacy"] = {
                    "has_readers": queue_ops.get('has_readers', False),
                    "has_writers": queue_ops.get('has_writers', False),
                    "connection_name": conn_info.get('connection_name', 'unknown'),
                    "application_name": conn_info.get('application_name', 'unknown'),
                    "channel_name": conn_info.get('channel_name', 'unknown')
                }
                parsed_data["operations"] = {
                    "get_count": queue_ops.get('get_count', 0),
                    "put_count": queue_ops.get('put_count', 0),
                    "browse_count": queue_ops.get('browse_count', 0),
                    "inquire_count": 0  # Would need additional parsing
                }
            else:
                # Fallback to basic parsing
                parsed_data.update({
                    "pcf_header_parsed": False,
                    "raw_message_preview": message[:100].hex()
                })
                
                # Use legacy parsing method
                reader_writer_info = self._identify_readers_writers(message)
                parsed_data.update(reader_writer_info)
                
            return parsed_data
            
        except (ValueError, IndexError, KeyError) as e:
            self.logger.error("Error parsing accounting message: %s", e)
            return None
    
    def _identify_statistics_type(self, message: bytes) -> str:
        """Identify the type of statistics message"""
        # This is a simplified implementation
        # In a production environment, you would parse the PCF parameters properly
        
        # Check for common statistics types based on message content patterns
        message_str = message.hex().upper()
        
        if "515441545354495155455545" in message_str:  # "STATSQUEUE" in hex
            return "queue_statistics"
        elif "53544154534348414E4E454C" in message_str:  # "STATSCHANNEL" in hex
            return "channel_statistics"
        elif "5354415453514D4752" in message_str:  # "STATSQMGR" in hex
            return "qmgr_statistics"
        else:
            return "unknown_statistics"
    
    def _identify_readers_writers(self, message: bytes) -> Dict[str, Any]:
        """Identify readers and writers from accounting message"""
        # This is a simplified implementation
        # In production, you would parse PCF parameters to get actual connection and operation details
        
        reader_writer_info = {
            "connection_info": {
                "has_readers": False,
                "has_writers": False,
                "connection_name": "unknown",
                "application_name": "unknown",
                "channel_name": "unknown"
            },
            "operations": {
                "get_count": 0,
                "put_count": 0,
                "browse_count": 0,
                "inquire_count": 0
            }
        }
        
        # Analyze message content for operation indicators
        message_hex = message.hex().upper()
        
        # Look for GET operations (readers)
        if "474554" in message_hex:  # "GET" in hex
            reader_writer_info["connection_info"]["has_readers"] = True
            reader_writer_info["operations"]["get_count"] = 1
        
        # Look for PUT operations (writers)
        if "505554" in message_hex:  # "PUT" in hex
            reader_writer_info["connection_info"]["has_writers"] = True
            reader_writer_info["operations"]["put_count"] = 1
        
        # Look for BROWSE operations
        if "42524F575345" in message_hex:  # "BROWSE" in hex
            reader_writer_info["operations"]["browse_count"] = 1
        
        return reader_writer_info
    
    def reset_statistics(self) -> bool:
        """Reset MQ statistics after reading"""
        if not STATS_CONFIG.get("reset_after_read", False):
            self.logger.info("Statistics reset disabled in configuration")
            return True
        
        try:
            # Create PCF message to reset statistics
            pcf = pymqi.PCFExecute(self.qmgr)
            
            # Reset queue manager statistics
            if STATS_CONFIG.get("collect_qmgr_stats", True):
                try:
                    pcf.MQCMD_RESET_Q_STATS({pymqi.CMQC.MQCA_Q_NAME: b"*"})
                    self.logger.info("Queue statistics reset successfully")
                except pymqi.MQMIError as e:
                    self.logger.warning("Failed to reset queue statistics: %s", e)
            
            # Reset channel statistics
            if STATS_CONFIG.get("collect_channel_stats", True):
                try:
                    pcf.MQCMD_RESET_CHANNEL_STATS({pymqi.CMQCFC.MQCACH_CHANNEL_NAME: b"*"})
                    self.logger.info("Channel statistics reset successfully")
                except pymqi.MQMIError as e:
                    self.logger.warning("Failed to reset channel statistics: %s", e)
            
            return True
            
        except pymqi.MQMIError as e:
            self.logger.error("Failed to reset statistics: %s", e)
            return False
        except (ValueError, TypeError) as e:
            self.logger.error("Data error during statistics reset: %s", e)
            return False
    
    def format_output(self, statistics_data: List[Dict], accounting_data: List[Dict]) -> str:
        """Format the collected data as JSON with timestamps"""
        output_data = {
            "collection_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "queue_manager": MQ_CONFIG["queue_manager"],
                "channel": MQ_CONFIG["channel"],
                "statistics_count": len(statistics_data),
                "accounting_count": len(accounting_data)
            },
            "statistics_data": statistics_data,
            "accounting_data": accounting_data,
            "summary": self._generate_summary(statistics_data, accounting_data)
        }
        
        if STATS_CONFIG.get("output_format", "json").lower() == "json":
            return json.dumps(output_data, indent=2, ensure_ascii=False)
        else:
            return str(output_data)
    
    def _generate_summary(self, statistics_data: List[Dict], accounting_data: List[Dict]) -> Dict[str, Any]:
        """Generate a summary of the collected data"""
        summary = {
            "total_messages": len(statistics_data) + len(accounting_data),
            "readers_identified": 0,
            "writers_identified": 0,
            "queue_operations": {
                "total_gets": 0,
                "total_puts": 0,
                "total_browses": 0
            },
            "active_connections": set(),
            "statistics_types": {}
        }
        
        # Analyze accounting data for readers/writers
        for acc_msg in accounting_data:
            conn_info = acc_msg.get("connection_info", {})
            if conn_info.get("has_readers"):
                summary["readers_identified"] += 1
            if conn_info.get("has_writers"):
                summary["writers_identified"] += 1
            
            operations = acc_msg.get("operations", {})
            summary["queue_operations"]["total_gets"] += operations.get("get_count", 0)
            summary["queue_operations"]["total_puts"] += operations.get("put_count", 0)
            summary["queue_operations"]["total_browses"] += operations.get("browse_count", 0)
        
        # Analyze statistics data
        for stat_msg in statistics_data:
            stat_type = stat_msg.get("statistics_type", "unknown")
            summary["statistics_types"][stat_type] = summary["statistics_types"].get(stat_type, 0) + 1
        
        # Convert set to list for JSON serialization
        summary["active_connections"] = list(summary["active_connections"])
        
        return summary
    
    def run(self) -> Optional[str]:
        """Main execution method"""
        self.logger.info("Starting MQ Statistics and Accounting Reader")
        
        # Connect to MQ
        if not self.connect_to_mq():
            return None
        
        try:
            # Read statistics and accounting data
            self.logger.info("Reading statistics queue...")
            statistics_data = self.read_statistics_queue()
            
            self.logger.info("Reading accounting queue...")
            accounting_data = self.read_accounting_queue()
            
            # Reset statistics if configured
            if STATS_CONFIG.get("reset_after_read", False):
                self.logger.info("Resetting statistics...")
                self.reset_statistics()
            
            # Format and return output
            output = self.format_output(statistics_data, accounting_data)
            self.logger.info("Data collection completed successfully")
            
            return output
            
        except (ValueError, TypeError, KeyError) as e:
            self.logger.error("Error during execution: %s", e)
            return None
        
        finally:
            self.disconnect_from_mq()


def main():
    """Main entry point"""
    reader = MQStatsReader()
    result = reader.run()
    
    if result:
        print("=== IBM MQ Statistics and Accounting Data ===")
        print(result)
        
        # Optionally save to file
        filename = f"mq_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\nData saved to {filename}")
    else:
        print("Failed to collect MQ statistics and accounting data")
        sys.exit(1)


if __name__ == "__main__":
    main()