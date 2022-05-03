import json
from database.omci_me_types import omci_me_class
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

me_to_yang_value = {
    'UNCOMMITTED': 'false',
    'COMMITTED': 'true',
    'INACTIVE': 'false',
    'ACTIVE': 'true',
    'INVALID': 'false',
    'VALID': 'true'
    }

def software_image_state(committed, active, valid):
    if active or committed:
        return "in-use"
    if valid:
        return "available"
    return "not-available"

def get_software_revisions(onu):
    onu_name = onu.onu_name
    sw_images = onu.get_all_instances(omci_me_class['SW_IMAGE'])
    result = {"revision" : []}
    for sw in sw_images:
        revision = {
            "id": sw.me_inst,
            "alias": onu_name + '-software-rev' + str(sw.me_inst),
            "state": software_image_state(me_to_yang_value[sw.is_committed], me_to_yang_value[sw.is_active], me_to_yang_value[sw.is_valid]),
            "version": sw.version.decode("utf-8"),
            "product-code": sw.product_code.decode("utf-8"),
            "hash": sw.image_hash.decode("utf-8"),
            "is-committed": me_to_yang_value[sw.is_committed],
            "is-active": me_to_yang_value[sw.is_active],
            "is-valid": me_to_yang_value[sw.is_valid]
        }
        result["revision"].append(revision)
    return result 
    
def get_yang_hardware_state(onu):
    onu_name = onu.onu_name
    revisions = get_software_revisions(onu)
    onu_g = onu.get_all_instances(omci_me_class['ONU_G'])
    onu2_g = onu.get_all_instances(omci_me_class['ONU2_G'])
    result = {
        "ietf-hardware-state:hardware": {
            "component": [
                {
                    "name": onu_name,
                    "model-name": onu2_g[0].equipment_id.decode("utf-8"),
                    "mfg-name": onu_g[0].vendor_id.decode("utf-8"),
                    "serial-num": onu_g[0].serial_number.decode("utf-8")
                }
            ]
        },
        "ietf-hardware:hardware": {
            "component": [
                {
                    "name": onu_name + '-software',
                    "bbf-software-management:software": {
                        "software": [
                            {
                                "name": onu_name,
                                "revisions": revisions
                            }
                        ]
                    }
                }
            ]
        }
    }
    return result 

def get_yang_response(onu):
    hardware_state = get_yang_hardware_state(onu)
    return json.dumps(hardware_state).replace('\\u0000', '').replace('\\u0016', '')
