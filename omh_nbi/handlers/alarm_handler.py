from math import floor
from signal import alarm
from time import sleep
from typing import Dict
from database.omci_onu_mib import OnuMib
from omh_nbi.notif_handler import NotificationHandler
from omci_types import RawMessage
from omci_logger import OmciLogger
from database.omci_me_types import omci_msg_type
from database.omci_me_types import omci_me_class
from database.omci_me_types import *
from database.omci_me import Alarm
import nbi.grpc.service_definition.tr451_vomci_nbi_message_pb2 as tr451_vomci_nbi_message_pb2
import struct
import datetime
import sys
import os
import json


VOLTMF_KAFKA_SENDER_NAME = (os.environ.get('VOMCI_KAFKA_SENDER_NAME'))
VOLTMF_KAFKA_VOLTMF_NAME = (os.environ.get('VOMCI_KAFKA_VOLTMF_NAME'))


logger = OmciLogger.getLogger(__name__)


class AlarmHandler(NotificationHandler):
   
    voltProducer = None
    seq_number = 0
    recv_get_all_alarms = False

    def notify_received_get_all_alarms():
        AlarmHandler.recv_get_all_alarms = True

    def recv(msg: RawMessage, onu):
        logger.info("Received alarm")

        dec=AlarmHandler.decode(msg,onu)
        if dec is not None:
            changed_alarms=dec[0]
            me=dec[1]
            inst=dec[2]
            
            AlarmHandler.sendAlarmtovOLTMF(me,onu,changed_alarms,inst)

        
    def decode(msg: RawMessage,onu):

        """Decode raw OMCI message
        Args:
            msg: raw OMCI message
        Returns:
            OnuDriver control block or None in case of error
        """  


        if len(msg) < 10:
            logger.error("decode: raw message is too short")
            return None

        # As an optimization only log a raw message if at debug level
        if logger.level <= logging.DEBUG:
            logger.debug("decode: ({})-{}".format(len(msg), ''.join(format(x, '02x') for x in msg)))

        tci, mt, dev, me_class, inst, alarm_bitmap, next_seq_number = struct.unpack_from('!HBBHH28s3xB', msg, 0)
        action = (mt & 0x1f)
        logger.info("action: %s" % omci_msg_type.value(action))
        logger.info("class: %s" % omci_me_class.value(me_class))
        logger.info("inst: %d" % inst)
        logger.info("alarm_bitmap: %r" % alarm_bitmap)
        logger.info("alarm_seqnum: %d" % next_seq_number)
 
        me = onu._main_mib.get(me_class=me_class,inst=inst)
        
        if me is None:
            #error not has class
            logger.warning("Me is None. Is needed add MIB to the ONU ")
            return None

        if not hasattr(me, 'alarms'):
            #error not has attr alarm
            logger.warning("Not hasattr 'alarms'")
            return None


        if not ((next_seq_number == 1 and AlarmHandler.seq_number == 255) or next_seq_number == AlarmHandler.seq_number + 1):
            logger.error("A loss has occurred in the alarm notification. The alarms are not aligned, is required an alarm resynchronization")
            AlarmHandler.sendMismatchtovOLTMF(onu, next_seq_number)
            return None
        
        AlarmHandler.seq_number = next_seq_number          

        changed_alarms=[]
        for idx in range(len(me.alarms)):
            byte = alarm_bitmap[floor(idx/8)]
            state = bool(byte & (1 << 7-idx%8))
            if not me.alarms[idx].get_state() == state:
                me.alarms[idx].set_state(state)
                changed_alarms.append(me.alarms[idx])
                logger.debug("State of alarm %d for inst %d me_class %r changed" % (idx,inst,me_class))

        onu._main_mib.set(me)
    
        logger.info("ME: %r", onu._main_mib.get(me_class,inst))   
        logger.info("(me_class: %r Inst: %d, Alarm: %r)\n" % (onu._main_mib.get_first(me_class),inst,onu._main_mib.get(me_class,inst).alarms))                                                                          
        
        if not AlarmHandler.recv_get_all_alarms:
            logger.info("Get_All_Alarms has not been received yet so alarm state is not changed and is not sent to vOLTMF ")   
            return None 

        return changed_alarms,me,inst

    def sendMismatchtovOLTMF(onu, next_seq_number):
        mismatch_msg = tr451_vomci_nbi_message_pb2.Msg()
        mismatch_msg.header.msg_id = "8"
        mismatch_msg.header.sender_name = VOLTMF_KAFKA_SENDER_NAME
        mismatch_msg.header.recipient_name = VOLTMF_KAFKA_VOLTMF_NAME
        mismatch_msg.header.object_type = mismatch_msg.header.ONU
        mismatch_msg.header.object_name = onu.onu_name

        mismatch_notif = {
            "bbf-vomci-function:onu-alarm-misalignment" : {
                "onu-name" : "",
                "detected-sequence-number" : ""

            }
        }

        mismatch_notif["bbf-vomci-function:onu-alarm-misalignment"]["onu-name"] = onu.onu_name
        mismatch_notif["bbf-vomci-function:onu-alarm-misalignment"]["detected-sequence-number"] = next_seq_number

        mismatch_not = json.dumps(mismatch_notif).replace('\\u0000', '').replace('\\u0016', '')

        mismatch_msg.body.notification.data = bytes(mismatch_not,'utf-8')
        logger.info('sending the SUCCESS protobuf response to VOLTMF:{}'.format(mismatch_msg))

        AlarmHandler.voltProducer.send_proto_notification(mismatch_msg)

    def sendAlarmtovOLTMF(me,onu,changed_alarms,inst):

        if AlarmHandler.voltProducer is None:
            #Workaround: uses values from environment variables. It is ok, because the kafka interface
            #usually never changes. Should get it from the KafkaInterface object inside the VOMCI instance.
            #However we don't have access to that object here.
            logger.info("AlarmHandler.voltProducer is None. Creating with defaults")
            import nbi.kafka_proto_interface as kafka_proto
            AlarmHandler.voltProducer = kafka_proto.VoltmfProtoProducer()
        
        perceived_severity = ""
        alarm_type_qualifier = "\"\""
        d = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        no_ms = d.replace(microsecond=0)
        time =  no_ms.isoformat() 
        
        alrm_msg = tr451_vomci_nbi_message_pb2.Msg()
        alrm_msg.header.msg_id="1"
        alrm_msg.header.sender_name= VOLTMF_KAFKA_SENDER_NAME
        alrm_msg.header.recipient_name= VOLTMF_KAFKA_VOLTMF_NAME
        alrm_msg.header.object_type=alrm_msg.header.ONU
        alrm_msg.header.object_name= onu.onu_name


        for alarm in changed_alarms:
            
            if ((alarm.resource == '/ietf-hardware:hardware/component')):
                name = me.hd_name
            elif ((alarm.resource == '/ietf-interfaces:interfaces/interface')):
                name = me.user_name
            else:
                logger.error("Error resource not recognized")
                return None
            
            if (name==None):
                logger.error("Resource not implemented")
                return None

            resource = alarm.resource+"[name='"+name+"']"

            logger.debug("\"resource\": %s", resource ) 
            logger.debug("\"alarm-type-id\": \"%s\"", alarm.name)
            if alarm.get_state() == False:
                perceived_severity = "cleared"
                alarm_descript = alarm._description + " cleared"
            else:
                perceived_severity = "major"
                alarm_descript = alarm._description + " detected"

            logger.debug("\"alarm-type-qualifier\": %s",alarm_type_qualifier)
            logger.debug("\"time\": %s", time)
            logger.debug("\"perceived-severity\": %s", perceived_severity)
            logger.debug("\"Alarm_text\": \"%s\"\n",  alarm_descript)

            alarm_notif = "{ \"ietf-alarms:alarm-notification\": {" + \
                 "\"resource\": " + "\"" + resource + "\"" + "," + \
                 "\"alarm-type-id\": " + "\"" + alarm.name + "\"" + "," +  \
                 "\"alarm-type-qualifier\": " +alarm_type_qualifier+ "," + \
                 "\"time\": " + "\"" + time + "\"" + "," + \
                 "\"perceived-severity\": " + "\"" + perceived_severity + "\"" + "," + \
                 "\"alarm-text\": " + "\"" + alarm_descript + "\"}}"

            alrm_msg.body.notification.data = bytes(alarm_notif,'utf-8')
            logger.info('sending the SUCCESS protobuf response to VOLTMF:{}'.format(alrm_msg))

            AlarmHandler.voltProducer.send_proto_notification(alrm_msg)
    

        
        
    

        


