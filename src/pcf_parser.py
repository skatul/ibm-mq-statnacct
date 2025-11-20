"""
PCF (Programmable Command Format) Message Parser for IBM MQ
This module provides utilities for parsing PCF messages from IBM MQ statistics and accounting queues.

PCF messages contain structured data about MQ operations, connections, and statistics.
"""

import struct
from typing import Dict, Any, List, Optional
import logging
from . import mq_constants as mqc


class PCFParser:
    """Parser for IBM MQ PCF (Programmable Command Format) messages"""
    
    # PCF Header Constants
    PCF_HEADER_SIZE = 36
    PCF_PARAMETER_HEADER_SIZE = 8
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_message(self, message: bytes) -> Optional[Dict[str, Any]]:
        """Parse a complete PCF message"""
        if len(message) < self.PCF_HEADER_SIZE:
            self.logger.warning("Message too short for PCF header")
            return None
        
        try:
            # Parse PCF header
            header = self._parse_pcf_header(message[:self.PCF_HEADER_SIZE])
            if not header:
                return None
            
            # Parse parameters
            parameters = self._parse_pcf_parameters(
                message[self.PCF_HEADER_SIZE:], 
                header.get('parameter_count', 0)
            )
            
            return {
                'header': header,
                'parameters': parameters,
                'message_size': len(message)
            }
            
        except (struct.error, ValueError, IndexError) as e:
            self.logger.error("Error parsing PCF message: %s", e)
            return None
    
    def _parse_pcf_header(self, header_bytes: bytes) -> Optional[Dict[str, Any]]:
        """Parse PCF message header"""
        try:
            # PCF header format (36 bytes):
            # Bytes 0-3: Structure type (MQLONG)
            # Bytes 4-7: Structure length (MQLONG)  
            # Bytes 8-11: Version (MQLONG)
            # Bytes 12-15: Command (MQLONG)
            # Bytes 16-19: Message sequence number (MQLONG)
            # Bytes 20-23: Control (MQLONG)
            # Bytes 24-27: Completion code (MQLONG)
            # Bytes 28-31: Reason code (MQLONG)
            # Bytes 32-35: Parameter count (MQLONG)
            
            values = struct.unpack('>9L', header_bytes)
            
            header = {
                'structure_type': values[0],
                'structure_length': values[1],
                'version': values[2],
                'command': values[3],
                'message_seq_number': values[4],
                'control': values[5],
                'completion_code': values[6],
                'reason_code': values[7],
                'parameter_count': values[8]
            }
            
            # Determine message type
            header['message_type'] = mqc.get_message_type(header['structure_type'])
            
            return header
            
        except struct.error as e:
            self.logger.error("Error unpacking PCF header: %s", e)
            return None
    

    
    def _parse_pcf_parameters(self, param_bytes: bytes, param_count: int) -> List[Dict[str, Any]]:
        """Parse PCF parameters from the message body"""
        parameters = []
        offset = 0
        
        for _ in range(param_count):
            if offset + self.PCF_PARAMETER_HEADER_SIZE > len(param_bytes):
                break
            
            param = self._parse_single_parameter(param_bytes[offset:])
            if param:
                parameters.append(param)
                offset += param.get('total_length', self.PCF_PARAMETER_HEADER_SIZE)
            else:
                break
        
        return parameters
    
    def _parse_single_parameter(self, param_bytes: bytes) -> Optional[Dict[str, Any]]:
        """Parse a single PCF parameter"""
        if len(param_bytes) < self.PCF_PARAMETER_HEADER_SIZE:
            return None
        
        try:
            # Parameter header format (8 bytes):
            # Bytes 0-3: Parameter identifier (MQLONG)
            # Bytes 4-7: Parameter type (MQLONG)
            
            param_id, param_type = struct.unpack('>LL', param_bytes[:8])
            
            parameter = {
                'parameter_id': param_id,
                'parameter_type': param_type,
                'parameter_name': mqc.get_parameter_name(param_id)
            }
            
            # Parse parameter value based on type
            if param_type == mqc.MQCFT_INTEGER:
                parameter.update(self._parse_integer_parameter(param_bytes))
            elif param_type == mqc.MQCFT_STRING:
                parameter.update(self._parse_string_parameter(param_bytes))
            elif param_type == mqc.MQCFT_BYTE_STRING:
                parameter.update(self._parse_byte_string_parameter(param_bytes))
            elif param_type == mqc.MQCFT_INTEGER_LIST:
                parameter.update(self._parse_integer_list_parameter(param_bytes))
            else:
                parameter['value'] = f'unsupported_type_{param_type}'
                parameter['total_length'] = self.PCF_PARAMETER_HEADER_SIZE
            
            return parameter
            
        except struct.error as e:
            self.logger.error("Error parsing PCF parameter: %s", e)
            return None
    
    def _parse_integer_parameter(self, param_bytes: bytes) -> Dict[str, Any]:
        """Parse integer parameter (12 bytes total)"""
        # Integer parameter: 8-byte header + 4-byte value
        if len(param_bytes) >= 12:
            value = struct.unpack('>L', param_bytes[8:12])[0]
            return {'value': value, 'total_length': 12}
        return {'value': 0, 'total_length': 12}
    
    def _parse_string_parameter(self, param_bytes: bytes) -> Dict[str, Any]:
        """Parse string parameter"""
        if len(param_bytes) >= 12:
            # String parameter: 8-byte header + 4-byte length + string data
            str_length = struct.unpack('>L', param_bytes[8:12])[0]
            total_length = 12 + str_length
            
            if len(param_bytes) >= total_length:
                try:
                    value = param_bytes[12:12+str_length].decode('utf-8').rstrip('\x00')
                    return {'value': value, 'total_length': total_length}
                except UnicodeDecodeError:
                    # Try with latin-1 if utf-8 fails
                    value = param_bytes[12:12+str_length].decode('latin-1').rstrip('\x00')
                    return {'value': value, 'total_length': total_length}
        
        return {'value': '', 'total_length': 12}
    
    def _parse_byte_string_parameter(self, param_bytes: bytes) -> Dict[str, Any]:
        """Parse byte string parameter"""
        if len(param_bytes) >= 12:
            data_length = struct.unpack('>L', param_bytes[8:12])[0]
            total_length = 12 + data_length
            
            if len(param_bytes) >= total_length:
                value = param_bytes[12:12+data_length]
                return {'value': value.hex(), 'total_length': total_length}
        
        return {'value': '', 'total_length': 12}
    
    def _parse_integer_list_parameter(self, param_bytes: bytes) -> Dict[str, Any]:
        """Parse integer list parameter"""
        if len(param_bytes) >= 12:
            count = struct.unpack('>L', param_bytes[8:12])[0]
            total_length = 12 + (count * 4)
            
            if len(param_bytes) >= total_length:
                values = []
                for i in range(count):
                    offset = 12 + (i * 4)
                    value = struct.unpack('>L', param_bytes[offset:offset+4])[0]
                    values.append(value)
                return {'value': values, 'total_length': total_length}
        
        return {'value': [], 'total_length': 12}
    
    def get_parameter_name(self, param_id: int) -> str:
        """Get human-readable parameter name from parameter ID"""
        return mqc.get_parameter_name(param_id)
    
    def extract_queue_operations(self, parsed_message: Dict[str, Any]) -> Dict[str, Any]:
        """Extract queue operation statistics from parsed message"""
        operations = {
            'queue_name': 'unknown',
            'get_count': 0,
            'put_count': 0,
            'browse_count': 0,
            'open_input_count': 0,
            'open_output_count': 0,
            'enqueue_count': 0,
            'dequeue_count': 0,
            'current_depth': 0,
            'max_depth': 0,
            'put_bytes': 0,
            'get_bytes': 0,
            'put_time': 0,
            'get_time': 0
        }
        
        if not parsed_message or 'parameters' not in parsed_message:
            return operations
        
        for param in parsed_message['parameters']:
            param_name = param.get('parameter_name', '')
            value = param.get('value')
            
            # Handle different value types safely
            if value is None:
                continue
                
            try:
                if param_name == 'MQCA_Q_NAME' and isinstance(value, str):
                    operations['queue_name'] = value.strip()
                elif param_name in ['MQIA_GET_COUNT'] and isinstance(value, int):
                    operations['get_count'] = value
                elif param_name in ['MQIA_PUT_COUNT'] and isinstance(value, int):
                    operations['put_count'] = value
                elif param_name in ['MQIA_BROWSE_COUNT'] and isinstance(value, int):
                    operations['browse_count'] = value
                elif param_name in ['MQIA_OPEN_INPUT_COUNT'] and isinstance(value, int):
                    operations['open_input_count'] = value
                elif param_name in ['MQIA_OPEN_OUTPUT_COUNT'] and isinstance(value, int):
                    operations['open_output_count'] = value
                elif param_name in ['MQIA_MSG_ENQ_COUNT'] and isinstance(value, int):
                    operations['enqueue_count'] = value
                elif param_name in ['MQIA_MSG_DEQ_COUNT'] and isinstance(value, int):
                    operations['dequeue_count'] = value
                elif param_name in ['MQIA_CURRENT_Q_DEPTH'] and isinstance(value, int):
                    operations['current_depth'] = value
                elif param_name in ['MQIA_MAX_Q_DEPTH'] and isinstance(value, int):
                    operations['max_depth'] = value
                elif param_name in ['MQIA_PUT_BYTES'] and isinstance(value, int):
                    operations['put_bytes'] = value
                elif param_name in ['MQIA_GET_BYTES'] and isinstance(value, int):
                    operations['get_bytes'] = value
                elif param_name in ['MQIA_PUT_TIME'] and isinstance(value, int):
                    operations['put_time'] = value
                elif param_name in ['MQIA_GET_TIME'] and isinstance(value, int):
                    operations['get_time'] = value
            except (ValueError, TypeError) as e:
                self.logger.warning("Error processing parameter %s with value %s: %s", 
                                  param_name, value, e)
                continue
        
        # Determine if there are readers and writers
        operations['has_readers'] = (operations['get_count'] > 0 or 
                                   operations['browse_count'] > 0 or 
                                   operations['open_input_count'] > 0)
        operations['has_writers'] = (operations['put_count'] > 0 or 
                                   operations['open_output_count'] > 0)
        
        return operations
    
    def extract_connection_info(self, parsed_message: Dict[str, Any]) -> Dict[str, Any]:
        """Extract connection information from parsed message"""
        connection_info = {
            'channel_name': 'unknown',
            'connection_name': 'unknown',
            'application_name': 'unknown',
            'user_id': 'unknown',
            'connect_count': 0,
            'disconnect_count': 0,
            'channel_type': 'unknown',
            'transport_type': 'unknown',
            'channel_status': 'unknown'
        }
        
        if not parsed_message or 'parameters' not in parsed_message:
            return connection_info
        
        for param in parsed_message['parameters']:
            param_name = param.get('parameter_name', '')
            value = param.get('value')
            
            if value is None:
                continue
                
            try:
                if param_name in ['MQCACH_CHANNEL_NAME'] and isinstance(value, str):
                    connection_info['channel_name'] = value.strip()
                elif param_name in ['MQCACH_CONNECTION_NAME'] and isinstance(value, str):
                    connection_info['connection_name'] = value.strip()
                elif param_name in ['MQCA_APPL_NAME'] and isinstance(value, str):
                    connection_info['application_name'] = value.strip()
                elif param_name in ['MQCACH_USER_ID'] and isinstance(value, str):
                    connection_info['user_id'] = value.strip()
                elif param_name in ['MQIA_CONNECT_COUNT'] and isinstance(value, int):
                    connection_info['connect_count'] = value
                elif param_name in ['MQIA_DISC_COUNT'] and isinstance(value, int):
                    connection_info['disconnect_count'] = value
                elif param_name in ['MQIACH_CHANNEL_TYPE'] and isinstance(value, int):
                    connection_info['channel_type'] = self._get_channel_type_name(value)
                elif param_name in ['MQIACH_TRANSPORT_TYPE'] and isinstance(value, int):
                    connection_info['transport_type'] = self._get_transport_type_name(value)
                elif param_name in ['MQIACH_CHANNEL_STATUS'] and isinstance(value, int):
                    connection_info['channel_status'] = self._get_channel_status_name(value)
            except (ValueError, TypeError) as e:
                self.logger.warning("Error processing connection parameter %s with value %s: %s", 
                                  param_name, value, e)
                continue
        
        return connection_info
    
    def _get_channel_type_name(self, channel_type: int) -> str:
        """Convert channel type integer to readable name"""
        return mqc.get_channel_type_name(channel_type)
    
    def _get_transport_type_name(self, transport_type: int) -> str:
        """Convert transport type integer to readable name"""
        return mqc.get_transport_type_name(transport_type)
    
    def _get_channel_status_name(self, status: int) -> str:
        """Convert channel status integer to readable name"""
        return mqc.get_channel_status_name(status)