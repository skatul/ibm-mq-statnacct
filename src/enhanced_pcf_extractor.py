"""
Enhanced PCF Data Extractor for Application Tags and Client IP

This module provides enhanced parsing capabilities for IBM MQ PCF accounting data
to extract application names, client IP addresses, and connection information
even when dealing with corrupted or malformed PCF messages.

Key Features:
- Robust application name extraction from binary PCF data
- Client IP address identification from connection strings
- Fallback parsing for corrupted PCF headers
- Application tag cleanup and normalization
- Connection name parsing for IP/port extraction
"""

import struct
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedPCFExtractor:
    """Enhanced PCF data extractor for application tags and client IPs"""
    
    def __init__(self):
        self.pcf_constants = {
            # PCF Parameter IDs for application information
            'MQCA_APPL_NAME': 2001,
            'MQCA_CONN_NAME': 2003,
            'MQCA_CHANNEL_NAME': 2004,
            'MQCA_USER_IDENTIFIER': 2005,
            'MQCA_APPL_TAG': 2011,
            'MQIA_APPL_TYPE': 1001,
            'MQIA_CONNECT_TYPE': 1002,
            'MQIACF_CONNECTION_NAME': 1269,
            'MQCACF_APPL_NAME': 3001,
            'MQCACF_USER_IDENTIFIER': 3002,
            'MQCACF_CONN_NAME': 3003,
            'MQCACF_CHANNEL_NAME': 3004,
            'MQCACF_APPL_TAG': 3011,
            
            # Operation types
            'MQPUT': 1,
            'MQGET': 2,
            'MQOPEN': 3,
            'MQCLOSE': 4,
        }
        
        # Common application name patterns
        self.app_name_patterns = [
            rb'([a-zA-Z0-9_\-\.]+\.exe)\x00',  # Windows executables
            rb'([a-zA-Z0-9_\-\.]+\.jar)\x00',  # Java applications
            rb'([a-zA-Z0-9_\-\.]+\.py)\x00',   # Python scripts
            rb'amqsput\x00',                    # IBM MQ sample PUT
            rb'amqsget\x00',                    # IBM MQ sample GET
            rb'generate_mq_activity\.py\x00',   # Our test script
            rb'reader_writer_demo\.py\x00',     # Our demo script
        ]
        
        # IP address pattern
        self.ip_pattern = re.compile(rb'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
        
        # Connection name pattern (IP:PORT or IP(PORT))
        self.conn_pattern = re.compile(rb'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\(\:](\d+)[\)\x00]?')
        
    def extract_application_info(self, message_data: bytes) -> Dict[str, Any]:
        """
        Extract application information from PCF message data
        
        Args:
            message_data: Raw PCF message bytes
            
        Returns:
            Dictionary containing extracted application information
        """
        
        info = {
            'application_name': 'unknown',
            'application_tag': 'unknown',
            'client_ip': 'unknown',
            'connection_name': 'unknown',
            'channel_name': 'unknown',
            'user_id': 'unknown',
            'extraction_method': 'none',
            'raw_data_found': False
        }
        
        try:
            # Try structured PCF parsing first
            structured_info = self._parse_structured_pcf(message_data)
            if structured_info['raw_data_found']:
                info.update(structured_info)
                return info
            
            # Fall back to pattern-based extraction
            pattern_info = self._extract_by_patterns(message_data)
            if pattern_info['raw_data_found']:
                info.update(pattern_info)
                return info
                
            # Final fallback - brute force search
            brute_force_info = self._brute_force_extraction(message_data)
            info.update(brute_force_info)
            
            return info
            
        except Exception as e:
            logger.warning(f"Error extracting application info: {e}")
            return info
    
    def _parse_structured_pcf(self, data: bytes) -> Dict[str, Any]:
        """Try to parse PCF data using structured approach"""
        
        info = {
            'application_name': 'unknown',
            'client_ip': 'unknown', 
            'extraction_method': 'structured_pcf',
            'raw_data_found': False
        }
        
        try:
            # Skip PCF header (first 36 bytes typically)
            offset = 36
            
            while offset < len(data) - 8:
                try:
                    # Read parameter header
                    param_type, param_length = struct.unpack('>II', data[offset:offset+8])
                    
                    if param_length < 8 or param_length > len(data) - offset:
                        break
                        
                    # Extract parameter data
                    param_data = data[offset+8:offset+param_length]
                    
                    # Check for application name parameters
                    if param_type in [2001, 3001]:  # MQCA_APPL_NAME, MQCACF_APPL_NAME
                        app_name = self._extract_string_parameter(param_data)
                        if app_name and app_name != 'unknown':
                            info['application_name'] = app_name
                            info['raw_data_found'] = True
                    
                    # Check for connection name parameters
                    elif param_type in [2003, 3003, 1269]:  # Connection name parameters
                        conn_name = self._extract_string_parameter(param_data)
                        if conn_name and conn_name != 'unknown':
                            # Extract IP from connection name
                            ip_match = self.ip_pattern.search(conn_name.encode())
                            if ip_match:
                                info['client_ip'] = ip_match.group(1).decode()
                                info['connection_name'] = conn_name
                                info['raw_data_found'] = True
                    
                    offset += param_length
                    
                except struct.error:
                    break
                    
            return info
            
        except Exception as e:
            logger.debug(f"Structured PCF parsing failed: {e}")
            return info
    
    def _extract_by_patterns(self, data: bytes) -> Dict[str, Any]:
        """Extract information using regex patterns"""
        
        info = {
            'application_name': 'unknown',
            'client_ip': 'unknown',
            'extraction_method': 'pattern_matching',
            'raw_data_found': False
        }
        
        # Search for application names
        for pattern in self.app_name_patterns:
            match = re.search(pattern, data)
            if match:
                app_name = match.group(1).decode('utf-8', errors='ignore')
                if app_name:
                    info['application_name'] = app_name.strip()
                    info['raw_data_found'] = True
                    logger.debug(f"Found application name via pattern: {app_name}")
                    break
        
        # Search for IP addresses and connection names
        conn_match = self.conn_pattern.search(data)
        if conn_match:
            ip = conn_match.group(1).decode()
            port = conn_match.group(2).decode()
            info['client_ip'] = ip
            info['connection_name'] = f"{ip}({port})"
            info['raw_data_found'] = True
            logger.debug(f"Found connection via pattern: {ip}({port})")
        else:
            # Just look for IP addresses
            ip_match = self.ip_pattern.search(data)
            if ip_match:
                info['client_ip'] = ip_match.group(1).decode()
                info['raw_data_found'] = True
                logger.debug(f"Found IP via pattern: {info['client_ip']}")
        
        return info
    
    def _brute_force_extraction(self, data: bytes) -> Dict[str, Any]:
        """Brute force search for application and connection data"""
        
        info = {
            'application_name': 'unknown',
            'client_ip': 'unknown',
            'extraction_method': 'brute_force',
            'raw_data_found': False
        }
        
        try:
            # Look for printable strings that might be application names
            text_data = data.decode('utf-8', errors='ignore')
            
            # Common application patterns
            app_patterns = [
                r'([a-zA-Z0-9_\-\.]+\.exe)',
                r'([a-zA-Z0-9_\-\.]+\.jar)', 
                r'([a-zA-Z0-9_\-\.]+\.py)',
                r'(amqsput)',
                r'(amqsget)',
                r'(generate_mq_activity)',
                r'(reader_writer_demo)'
            ]
            
            for pattern in app_patterns:
                match = re.search(pattern, text_data, re.IGNORECASE)
                if match:
                    info['application_name'] = match.group(1)
                    info['raw_data_found'] = True
                    logger.debug(f"Found application via brute force: {match.group(1)}")
                    break
            
            # Look for IP addresses in text
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', text_data)
            if ip_match:
                info['client_ip'] = ip_match.group(1)
                info['raw_data_found'] = True
                logger.debug(f"Found IP via brute force: {ip_match.group(1)}")
            
            return info
            
        except Exception as e:
            logger.debug(f"Brute force extraction failed: {e}")
            return info
    
    def _extract_string_parameter(self, param_data: bytes) -> Optional[str]:
        """Extract string from PCF parameter data"""
        
        try:
            # Remove null bytes and decode
            clean_data = param_data.rstrip(b'\x00')
            if len(clean_data) > 0:
                return clean_data.decode('utf-8', errors='ignore').strip()
            return None
        except Exception:
            return None
    
    def extract_reader_writer_info(self, accounting_messages: List[Dict]) -> Dict[str, Any]:
        """
        Extract reader/writer information from accounting messages
        
        Args:
            accounting_messages: List of accounting message dictionaries
            
        Returns:
            Dictionary with reader/writer analysis
        """
        
        analysis = {
            'applications': {},
            'readers': {},
            'writers': {},
            'client_ips': set(),
            'connection_summary': {},
            'extraction_stats': {
                'total_messages': len(accounting_messages),
                'successful_extractions': 0,
                'failed_extractions': 0,
                'corrupted_messages': 0
            }
        }
        
        for msg in accounting_messages:
            try:
                # Check if message is corrupted
                pcf_data = msg.get('pcf_data', {})
                header = pcf_data.get('header', {})
                
                if header.get('corruption_detected', False):
                    analysis['extraction_stats']['corrupted_messages'] += 1
                    logger.debug("Skipping corrupted message for extraction")
                    continue
                
                # Get raw message data if available
                message_length = msg.get('message_length', 0)
                if message_length > 0 and 'raw_data' in msg:
                    # Extract from raw data
                    app_info = self.extract_application_info(msg['raw_data'])
                else:
                    # Try to extract from available structured data
                    app_info = self._extract_from_structured_msg(msg)
                
                if app_info['raw_data_found']:
                    analysis['extraction_stats']['successful_extractions'] += 1
                    
                    app_name = app_info['application_name']
                    client_ip = app_info['client_ip']
                    
                    # Track application
                    if app_name != 'unknown':
                        if app_name not in analysis['applications']:
                            analysis['applications'][app_name] = {
                                'client_ip': client_ip,
                                'operations': {'put': 0, 'get': 0, 'open': 0, 'close': 0},
                                'queues_accessed': set(),
                                'first_seen': datetime.now().isoformat(),
                                'connection_info': app_info
                            }
                        
                        # Determine if reader or writer based on operations
                        operations = msg.get('operations', {})
                        put_count = operations.get('put_count', 0)
                        get_count = operations.get('get_count', 0)
                        
                        if put_count > 0:
                            analysis['writers'][app_name] = analysis['applications'][app_name]
                        if get_count > 0:
                            analysis['readers'][app_name] = analysis['applications'][app_name]
                        
                        # Track client IP
                        if client_ip != 'unknown':
                            analysis['client_ips'].add(client_ip)
                            
                            if client_ip not in analysis['connection_summary']:
                                analysis['connection_summary'][client_ip] = {
                                    'applications': set(),
                                    'total_operations': 0,
                                    'connection_name': app_info.get('connection_name', 'unknown')
                                }
                            
                            analysis['connection_summary'][client_ip]['applications'].add(app_name)
                            analysis['connection_summary'][client_ip]['total_operations'] += put_count + get_count
                
                else:
                    analysis['extraction_stats']['failed_extractions'] += 1
                    
            except Exception as e:
                analysis['extraction_stats']['failed_extractions'] += 1
                logger.warning(f"Error processing accounting message: {e}")
        
        # Convert sets to lists for JSON serialization
        analysis['client_ips'] = list(analysis['client_ips'])
        for app_info in analysis['applications'].values():
            app_info['queues_accessed'] = list(app_info['queues_accessed'])
        for conn_info in analysis['connection_summary'].values():
            conn_info['applications'] = list(conn_info['applications'])
            
        return analysis
    
    def _extract_from_structured_msg(self, msg: Dict) -> Dict[str, Any]:
        """Extract application info from structured message data"""
        
        info = {
            'application_name': 'unknown',
            'client_ip': 'unknown',
            'extraction_method': 'structured_msg',
            'raw_data_found': False
        }
        
        # Check connection info
        conn_info = msg.get('connection_info', {})
        if conn_info:
            app_name = conn_info.get('application_name', 'unknown')
            conn_name = conn_info.get('connection_name', 'unknown')
            
            if app_name != 'unknown':
                info['application_name'] = app_name
                info['raw_data_found'] = True
                
            if conn_name != 'unknown':
                # Try to extract IP from connection name
                ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', conn_name)
                if ip_match:
                    info['client_ip'] = ip_match.group(1)
                    info['connection_name'] = conn_name
                    info['raw_data_found'] = True
        
        return info

def create_enhanced_extractor() -> EnhancedPCFExtractor:
    """Create and return an enhanced PCF extractor instance"""
    return EnhancedPCFExtractor()

if __name__ == "__main__":
    # Test the extractor
    logging.basicConfig(level=logging.DEBUG)
    
    extractor = EnhancedPCFExtractor()
    
    # Test with sample data
    test_data = b"amqsput.exe\x00\x00\x00192.168.1.100(1414)\x00"
    
    result = extractor.extract_application_info(test_data)
    print("Test extraction result:")
    print(f"Application: {result['application_name']}")
    print(f"Client IP: {result['client_ip']}")
    print(f"Method: {result['extraction_method']}")
    print(f"Success: {result['raw_data_found']}")