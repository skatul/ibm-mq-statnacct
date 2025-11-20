"""
PCF (Programmable Command Format) Message Parser for IBM MQ
This module provides utilities for parsing PCF messages from IBM MQ statistics and accounting queues.

PCF messages contain structured data about MQ operations, connections, and statistics.
"""

import struct
from typing import Dict, Any, List, Optional
import logging


class PCFParser:
    """Parser for IBM MQ PCF (Programmable Command Format) messages"""
    
    # PCF Header Constants
    PCF_HEADER_SIZE = 36
    PCF_PARAMETER_HEADER_SIZE = 8
    
    # PCF Structure Types
    MQCFT_NONE = 0
    MQCFT_COMMAND = 1
    MQCFT_RESPONSE = 2
    MQCFT_INTEGER = 3
    MQCFT_STRING = 4
    MQCFT_INTEGER_LIST = 5
    MQCFT_STRING_LIST = 6
    MQCFT_EVENT = 7
    MQCFT_USER = 8
    MQCFT_BYTE_STRING = 9
    MQCFT_TRACE_ROUTE = 10
    MQCFT_REPORT = 11
    MQCFT_INTEGER_FILTER = 12
    MQCFT_STRING_FILTER = 13
    MQCFT_BYTE_STRING_FILTER = 14
    MQCFT_COMMAND_XR = 16
    MQCFT_XR_MSG = 17
    MQCFT_XR_ITEM = 18
    MQCFT_XR_SUMMARY = 19
    MQCFT_GROUP = 20
    MQCFT_STATISTICS = 21
    MQCFT_ACCOUNTING = 22
    
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
            header['message_type'] = self._determine_message_type(header['structure_type'])
            
            return header
            
        except struct.error as e:
            self.logger.error("Error unpacking PCF header: %s", e)
            return None
    
    def _determine_message_type(self, structure_type: int) -> str:
        """Determine the type of PCF message based on structure type"""
        type_map = {
            self.MQCFT_STATISTICS: 'statistics',
            self.MQCFT_ACCOUNTING: 'accounting',
            self.MQCFT_EVENT: 'event',
            self.MQCFT_COMMAND: 'command',
            self.MQCFT_RESPONSE: 'response',
            self.MQCFT_REPORT: 'report'
        }
        return type_map.get(structure_type, f'unknown_type_{structure_type}')
    
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
                'parameter_name': self.get_parameter_name(param_id)
            }
            
            # Parse parameter value based on type
            if param_type == self.MQCFT_INTEGER:
                parameter.update(self._parse_integer_parameter(param_bytes))
            elif param_type == self.MQCFT_STRING:
                parameter.update(self._parse_string_parameter(param_bytes))
            elif param_type == self.MQCFT_BYTE_STRING:
                parameter.update(self._parse_byte_string_parameter(param_bytes))
            elif param_type == self.MQCFT_INTEGER_LIST:
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
        # Comprehensive IBM MQ parameter IDs mapping
        param_names = {
            # Character attributes (MQCA_*)
            2001: 'MQCA_Q_NAME',
            2002: 'MQCA_Q_MGR_NAME',
            2003: 'MQCA_PROCESS_NAME', 
            2004: 'MQCA_TRIGGER_DATA',
            2005: 'MQCA_Q_DESC',
            2006: 'MQCA_CREATION_DATE',
            2007: 'MQCA_CREATION_TIME',
            2008: 'MQCA_ALTERATION_DATE',
            2009: 'MQCA_ALTERATION_TIME',
            2010: 'MQCA_BACKOUT_REQ_Q_NAME',
            2011: 'MQCA_INITIATION_Q_NAME',
            2012: 'MQCA_DEAD_LETTER_Q_NAME',
            2013: 'MQCA_DEF_XMIT_Q_NAME',
            2014: 'MQCA_CF_STRUC_NAME',
            2015: 'MQCA_QSG_NAME',
            2016: 'MQCA_STORAGE_CLASS',
            2017: 'MQCA_XCFGNAME',
            2018: 'MQCA_XCFMNAME',
            2019: 'MQCA_COMMAND_MQSC',
            2020: 'MQCA_Q_MGR_IDENTIFIER',
            2021: 'MQCA_CLUSTER_NAME',
            2022: 'MQCA_CLUSTER_NAMELIST',
            2023: 'MQCA_CLUSTER_Q_MGR_NAME',
            2024: 'MQCA_CLUS_CHL_NAME',
            2025: 'MQCA_AUTH_INFO_NAME',
            2026: 'MQCA_AUTH_INFO_DESC',
            2027: 'MQCA_LDAP_USER_NAME',
            2028: 'MQCA_AUTH_INFO_CONN_NAME',
            2029: 'MQCA_LDAP_PASSWORD',
            2030: 'MQCA_SSL_CRL_NAMELIST',
            2031: 'MQCA_SSL_CRYPTO_HARDWARE',
            2032: 'MQCA_SSL_KEY_REPOSITORY',
            2033: 'MQCA_SSL_KEY_MEMBER',
            2034: 'MQCA_SSL_CIPHER_SPEC',
            2035: 'MQCA_SSL_PEER_NAME',
            2036: 'MQCA_SSL_CLIENT_AUTH',
            
            # Channel character attributes (MQCACH_*)
            3501: 'MQCACH_CHANNEL_NAME',
            3502: 'MQCACH_DESC',
            3503: 'MQCACH_MODE_NAME', 
            3504: 'MQCACH_TP_NAME',
            3505: 'MQCACH_CONNECTION_NAME',
            3506: 'MQCACH_XMIT_Q_NAME',
            3507: 'MQCACH_CLUSTER_NAME',
            3508: 'MQCACH_CLUSTER_NAMELIST',
            3509: 'MQCACH_MODENAME',
            3510: 'MQCACH_USER_ID',
            3511: 'MQCACH_PASSWORD',
            3512: 'MQCACH_LOCAL_ADDRESS',
            3513: 'MQCACH_LOCAL_NAME',
            3514: 'MQCACH_LAST_MSG_TIME',
            3515: 'MQCACH_LAST_MSG_DATE',
            3516: 'MQCACH_MCA_NAME',
            3517: 'MQCACH_MCA_TYPE',
            3518: 'MQCACH_MCA_USER_ID',
            3519: 'MQCACH_NETWORK_PRIORITY',
            3520: 'MQCACH_SEQUENCE_NUMBER_WRAP',
            3521: 'MQCACH_MAX_MSG_LENGTH',
            3522: 'MQCACH_PUT_AUTHORITY',
            3523: 'MQCACH_DATA_CONVERSION',
            3524: 'MQCACH_SECURITY_EXIT',
            3525: 'MQCACH_MSG_EXIT',
            3526: 'MQCACH_SEND_EXIT',
            3527: 'MQCACH_RECEIVE_EXIT',
            3528: 'MQCACH_SEQ_NUMBER_WRAP',
            3529: 'MQCACH_MAX_MSG_LENGTH',
            3530: 'MQCACH_PUT_AUTHORITY',
            3531: 'MQCACH_DATA_CONVERSION',
            3532: 'MQCACH_SECURITY_EXIT_NAME',
            3533: 'MQCACH_MSG_EXIT_NAME',
            3534: 'MQCACH_SEND_EXIT_NAME',
            3535: 'MQCACH_RECEIVE_EXIT_NAME',
            3536: 'MQCACH_CHANNEL_AUTO_DEF_EXIT',
            3537: 'MQCACH_CHANNEL_AUTO_DEF_EVENT',
            3538: 'MQCACH_SSL_CIPHER_SPEC',
            3539: 'MQCACH_SSL_PEER_NAME',
            3540: 'MQCACH_SSL_CLIENT_AUTH',
            
            # Integer attributes (MQIA_*)
            1: 'MQIA_Q_TYPE',
            2: 'MQIA_MAX_Q_DEPTH', 
            3: 'MQIA_MAX_MSG_LENGTH',
            4: 'MQIA_BACKOUT_THRESHOLD',
            5: 'MQIA_SHAREABILITY',
            6: 'MQIA_DEF_SHAREABILITY',
            7: 'MQIA_HARDEN_GET_BACKOUT',
            8: 'MQIA_MSG_DELIVERY_SEQUENCE',
            9: 'MQIA_RETENTION_INTERVAL',
            10: 'MQIA_Q_DEPTH_HIGH_EVENT',
            11: 'MQIA_Q_DEPTH_LOW_EVENT',
            12: 'MQIA_Q_SERVICE_INTERVAL_EVENT',
            13: 'MQIA_Q_DEPTH_MAX_EVENT',
            14: 'MQIA_CURRENT_Q_DEPTH',
            15: 'MQIA_OPEN_INPUT_COUNT',
            16: 'MQIA_OPEN_OUTPUT_COUNT',
            17: 'MQIA_HIGH_Q_DEPTH',
            18: 'MQIA_MSG_ENQ_COUNT',
            19: 'MQIA_MSG_DEQ_COUNT',
            20: 'MQIA_TIME_SINCE_RESET',
            21: 'MQIA_Q_DEPTH_HIGH_LIMIT',
            22: 'MQIA_Q_DEPTH_LOW_LIMIT',
            23: 'MQIA_Q_SERVICE_INTERVAL',
            24: 'MQIA_INHIBIT_PUT',
            25: 'MQIA_INHIBIT_GET',
            26: 'MQIA_TRIGGER_CONTROL',
            27: 'MQIA_TRIGGER_TYPE',
            28: 'MQIA_TRIGGER_DEPTH',
            29: 'MQIA_TRIGGER_MSG_PRIORITY',
            30: 'MQIA_DEF_PRIORITY',
            31: 'MQIA_DEF_PERSISTENCE',
            32: 'MQIA_DEF_INPUT_OPEN_OPTION',
            33: 'MQIA_DEF_BIND',
            34: 'MQIA_MAX_HANDLES',
            35: 'MQIA_MAX_UNCOMMITTED_MSGS',
            36: 'MQIA_SYNC_POINT',
            37: 'MQIA_DEFSOPT',
            38: 'MQIA_DEF_READ_AHEAD',
            39: 'MQIA_DEF_PROPERTY_CONTROL',
            40: 'MQIA_PROPERTY_CONTROL',
            41: 'MQIA_PAGESET_ID',
            42: 'MQIA_USAGE',
            43: 'MQIA_DEFINITION_TYPE',
            44: 'MQIA_CLUSTER_PUB_ROUTE',
            45: 'MQIA_CLUSTER_SUB_ROUTE',
            46: 'MQIA_CLUSTER_WORKLOAD_USEQ',
            47: 'MQIA_CLUSTER_WORKLOAD_RANK',
            48: 'MQIA_DISTL_BIND',
            49: 'MQIA_Q_MGR_STATUS',
            50: 'MQIA_PLATFORM',
            
            # Statistics and monitoring parameters
            51: 'MQIA_PUT_COUNT',
            52: 'MQIA_GET_COUNT', 
            53: 'MQIA_BROWSE_COUNT',
            54: 'MQIA_PUT1_COUNT',
            55: 'MQIA_CB_COUNT',
            56: 'MQIA_CTL_COUNT',
            57: 'MQIA_INQ_COUNT',
            58: 'MQIA_SET_COUNT',
            59: 'MQIA_CONNECT_COUNT',
            60: 'MQIA_DISC_COUNT',
            61: 'MQIA_OPEN_COUNT',
            62: 'MQIA_CLOSE_COUNT',
            63: 'MQIA_SUB_COUNT',
            64: 'MQIA_SUBRQ_COUNT',
            65: 'MQIA_CHL_COUNT',
            66: 'MQIA_CHL_TOTAL_BYTES',
            67: 'MQIA_CHL_TIME_INDICATOR',
            68: 'MQIA_CHL_BATCH_SIZE',
            69: 'MQIA_CHL_BATCH_INTERVAL',
            70: 'MQIA_CHL_LONG_RETRY_COUNT',
            71: 'MQIA_CHL_LONG_RETRY_INTERVAL',
            72: 'MQIA_CHL_SHORT_RETRY_COUNT', 
            73: 'MQIA_CHL_SHORT_RETRY_INTERVAL',
            74: 'MQIA_CHL_MCA_TYPE',
            75: 'MQIA_CHL_TRANSPORT_TYPE',
            76: 'MQIA_CHL_DATA_COUNT',
            77: 'MQIA_CHL_MAX_MSG_LENGTH',
            78: 'MQIA_CHL_NETWORK_PRIORITY',
            79: 'MQIA_CHL_SEQUENCE_NUMBER_WRAP',
            80: 'MQIA_CHL_PUT_AUTHORITY',
            
            # Channel integer attributes (MQIACH_*)
            1501: 'MQIACH_CHANNEL_TYPE',
            1502: 'MQIACH_TRANSPORT_TYPE',
            1503: 'MQIACH_DATA_COUNT',
            1504: 'MQIACH_NAME_COUNT',
            1505: 'MQIACH_MAX_MSG_LENGTH',
            1506: 'MQIACH_BATCH_SIZE',
            1507: 'MQIACH_BATCH_INTERVAL',
            1508: 'MQIACH_LONG_RETRY_COUNT',
            1509: 'MQIACH_LONG_RETRY_INTERVAL',
            1510: 'MQIACH_SHORT_RETRY_COUNT',
            1511: 'MQIACH_SHORT_RETRY_INTERVAL',
            1512: 'MQIACH_DISC_INTERVAL',
            1513: 'MQIACH_THRESHOLD',
            1514: 'MQIACH_PRIORITY',
            1515: 'MQIACH_DATA_CONVERSION',
            1516: 'MQIACH_SECURITY_EXIT_COUNT',
            1517: 'MQIACH_MSG_EXIT_COUNT',
            1518: 'MQIACH_SEND_EXIT_COUNT',
            1519: 'MQIACH_RECEIVE_EXIT_COUNT',
            1520: 'MQIACH_CHANNEL_INSTANCE_TYPE',
            1521: 'MQIACH_CHANNEL_INSTANCE_ATTRS',
            1522: 'MQIACH_SSL_CLIENT_AUTH',
            1523: 'MQIACH_KEEP_ALIVE_INTERVAL',
            1524: 'MQIACH_LOCAL_ADDRESS',
            1525: 'MQIACH_BATCH_HB',
            1526: 'MQIACH_HB_INTERVAL',
            1527: 'MQIACH_SHORT_TIMER',
            1528: 'MQIACH_BATCH_DATA_LIMIT',
            1529: 'MQIACH_FAST_PATH',
            1530: 'MQIACH_DEF_RECONNECT',
            1531: 'MQIACH_CHANNEL_STATUS',
            1532: 'MQIACH_INDOUBT_STATUS',
            1533: 'MQIACH_LAST_SEQ_NUMBER',
            1534: 'MQIACH_LAST_SEQUENCE_NUMBER',
            1535: 'MQIACH_CURRENT_SEQ_NUMBER',
            1536: 'MQIACH_CURRENT_SEQUENCE_NUMBER',
            1537: 'MQIACH_SSL_RETURN_CODE',
            1538: 'MQIACH_MSGS',
            1539: 'MQIACH_BYTES_SENT',
            1540: 'MQIACH_BYTES_RECEIVED',
            1541: 'MQIACH_BATCHES',
            1542: 'MQIACH_BUFFERS_SENT',
            1543: 'MQIACH_BUFFERS_RECEIVED',
            1544: 'MQIACH_LONG_RETRIES_LEFT',
            1545: 'MQIACH_SHORT_RETRIES_LEFT',
            1546: 'MQIACH_MCA_STATUS',
            1547: 'MQIACH_STOP_REQUESTED',
            1548: 'MQIACH_MR_COUNT',
            1549: 'MQIACH_MR_INTERVAL',
            
            # Common hexadecimal parameter IDs seen in real MQ environments
            842019381: 'MQIA_ACCOUNTING_CONN_OVERRIDE',  # 0x32300135
            842019382: 'MQIA_ACCOUNTING_INTERVAL',        # 0x32300136  
            842019383: 'MQIA_ACTIVITY_RECORDING',         # 0x32300137
            842019384: 'MQIA_ADOPTNEWMCA_CHECK',          # 0x32300138
            842019385: 'MQIA_ADOPTNEWMCA_TYPE',           # 0x32300139
            842019386: 'MQIA_ADOPTNEWMCA_INTERVAL',       # 0x3230013A
            842019387: 'MQIA_TRACE_ROUTE_RECORDING',      # 0x3230013B
            842019388: 'MQIA_STATISTICS_AUTO_CLUSSDR',    # 0x3230013C
            842019389: 'MQIA_STATISTICS_CHANNEL',         # 0x3230013D
            842019390: 'MQIA_STATISTICS_INTERVAL',        # 0x3230013E
            842019391: 'MQIA_STATISTICS_MQI',             # 0x3230013F
            842019392: 'MQIA_STATISTICS_Q',               # 0x32300140
            
            # Additional common parameter IDs
            167772161: 'MQCA_APPL_NAME',                  # 0x0A000001
            167772162: 'MQCA_APPL_IDENTITY_DATA',         # 0x0A000002
            167772163: 'MQCA_ENV_DATA',                   # 0x0A000003
            167772164: 'MQCA_USER_DATA',                  # 0x0A000004
            167772165: 'MQCA_ACCOUNTING_TOKEN',           # 0x0A000005
            167772166: 'MQCA_CONN_TAG',                   # 0x0A000006
            
            # Queue Manager attributes
            301989889: 'MQIA_COMMAND_LEVEL',              # 0x12000001  
            301989890: 'MQIA_Q_MGR_STATUS',               # 0x12000002
            301989891: 'MQIA_UNIT_OF_WORK_SIZE',          # 0x12000003
            301989892: 'MQIA_ACTIVE_CHANNELS',            # 0x12000004
            301989893: 'MQIA_ADOPTNEWMCA_ADVISE',         # 0x12000005
            301989894: 'MQIA_ADOPTNEWMCA_CHECK',          # 0x12000006
            301989895: 'MQIA_ADOPTNEWMCA_TYPE',           # 0x12000007
            
            # Performance and timing parameters
            536870912: 'MQIA_PUT_TIME',                   # 0x20000000
            536870913: 'MQIA_GET_TIME',                   # 0x20000001
            536870914: 'MQIA_BROWSE_TIME',                # 0x20000002
            536870915: 'MQIA_COMMIT_TIME',                # 0x20000003
            536870916: 'MQIA_ROLLBACK_TIME',              # 0x20000004
            
            # Message counts and sizes
            671088640: 'MQIA_PUT_BYTES',                  # 0x28000000
            671088641: 'MQIA_GET_BYTES',                  # 0x28000001
            671088642: 'MQIA_BROWSE_BYTES',               # 0x28000002
            671088643: 'MQIA_PUT_MEAN_SIZE',              # 0x28000003
            671088644: 'MQIA_GET_MEAN_SIZE',              # 0x28000004
        }
        
        # Check if parameter is unknown and log for debugging
        if param_id not in param_names:
            self.logger.debug("Unknown parameter ID encountered: %d (0x%08X)", param_id, param_id)
        
        return param_names.get(param_id, f'UNKNOWN_PARAM_{param_id}_0x{param_id:08X}')
    
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
        types = {
            1: 'SENDER',
            2: 'SERVER', 
            3: 'RECEIVER',
            4: 'REQUESTER',
            5: 'CLIENT_CONNECTION',
            6: 'SERVER_CONNECTION',
            7: 'CLUSTER_RECEIVER',
            8: 'CLUSTER_SENDER'
        }
        return types.get(channel_type, f'UNKNOWN_CHANNEL_TYPE_{channel_type}')
    
    def _get_transport_type_name(self, transport_type: int) -> str:
        """Convert transport type integer to readable name"""
        types = {
            1: 'LU62',
            2: 'TCP',
            3: 'NETBIOS',
            4: 'SPX',
            5: 'DECnet',
            6: 'UDP'
        }
        return types.get(transport_type, f'UNKNOWN_TRANSPORT_{transport_type}')
    
    def _get_channel_status_name(self, status: int) -> str:
        """Convert channel status integer to readable name"""
        statuses = {
            0: 'INACTIVE',
            1: 'BINDING',
            2: 'STARTING',
            3: 'RUNNING', 
            4: 'STOPPING',
            5: 'RETRYING',
            6: 'STOPPED',
            7: 'REQUESTING',
            8: 'PAUSED',
            13: 'INITIALIZING'
        }
        return statuses.get(status, f'UNKNOWN_STATUS_{status}')