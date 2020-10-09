## Test Programs

The following optional parameters are common for all test programs:<br>
**Common Optional Parameters**<br>
  -a POLT_HOST, --polt-host POLT_HOST; pOLT DNS name or IP address; default: 'localhost'<br>
  -p POLT_PORT, --polt-port POLT_PORT; pOLT UDP port number; default: 50000<br>
  -l LOGLEVEL, --loglevel LOGLEVEL; logging level (0=errors+warnings, 1=info, 2=debug); default: 1<br>
  -v VOMCI_NAME, --vomci-name VOMCI_NAME;  vOMCI name; default: 'vomci1'<br>
  -c CTERM_NAME, --cterm-name CTERM_NAME; channel-termination name; default: 'channeltermination.1'<br>
  -o ONU_ID, --onu-id ONU_ID. ONU id; default: 2<br>
  -t TCI, --tci TCI     Starting TCI value; default: 1<br>
  -b BACKGROUND, --background BACKGROUND; Run FSM in the background: False<br>
  -i ITERS, --iters ITERS; Number of times to execute the FSM: 1<br>
  -d DUMP_MIB, --dump-mib DUMP_MIB' Dump ONU MIB: False<br>
  --timeout TIMEOUT     Message timeout (s): 2.0<br>
  --retries RETRIES     Max number of retries: 2<br>


### bin/test_onu_fsm: Invoke any ONU FSM

**Usage**<br>
bin/test_onu_fsm [-h] [-f FSM] [-a POLT_HOST] [-p POLT_PORT] [-l LOGLEVEL]
                    [-v VOMCI_NAME] [-c CTERM_NAME] [-o ONU_ID] [-t TCI]
                    [-b BACKGROUND] [-i ITERS] [-d DUMP_MIB]

**Mandatory Parameters**<br>
  -f FSM, --fsm FSM     FSM to execute: MIB_RESET MIB_UPLOAD ACTIVATE_ONU<br>

**Extra Optional Parameters**<br>
None

### bin.test_activate_onu: Invoke ONU activation FSM

**Usage**<br>
bin/test_activate_onu [-h] [-a POLT_HOST] [-p POLT_PORT] [-l LOGLEVEL]
                         [-v VOMCI_NAME] [-c CTERM_NAME] [-o ONU_ID] [-t TCI]
                         [-b BACKGROUND] [-i ITERS] [-d DUMP_MIB]
                         [-r FORCE_RESET]

**Extra Optional Parameters:**<br>
  -r FORCE_RESET, --force-reset FORCE_RESET; Force ONU reset and re-sync: False<br>

### bin.test_uni_tcont_gem: Activate ONU and configure UNI, TCONT and GEM port
**Usage**<br>
bin/test_uni_tcont_gem [-h] [-a POLT_HOST] [-p POLT_PORT] [-l LOGLEVEL]
                          [-v VOMCI_NAME] [-c CTERM_NAME] [-o ONU_ID] [-t TCI]
                          [-b BACKGROUND] [-i ITERS] [-d DUMP_MIB]
                          [--uni-name UNI_NAME] [--uni-id UNI_ID]
                          [--tcont-name TCONT_NAME] [--alloc-id ALLOC_ID]
                          [--gemport-name GEMPORT_NAME]
                          [--gemport-id GEMPORT_ID] [--tc TC]
                          [--direction DIRECTION] [--encryption ENCRYPTION]

**Extra Optional Parameters:**<br>
  --uni-name UNI_NAME   UNI name: 'uni.1'<br>
  --uni-id UNI_ID       UNI id: 0<br>
  --tcont-name TCONT_NAME; TCONT name: 'tcont.1'<br>
  --alloc-id ALLOC_ID   ALLOC Id: 1024<br>
  --gemport-name GEMPORT_NAME; GEM port name: 'gem.1'<br>
  --gemport-id GEMPORT_ID; GEMPORT Id: 1025<br>
  --tc TC               Traffic Class: 1<br>
  --direction DIRECTION; GEM port direction: 'BIDIRECTIONAL'<br>
  --encryption ENCRYPTION; GEM port encryption: 'NO_ENCRYPTION'<br>

### bin.test_qos_policy_profile: Create QoS Policy Profile

This test performs the following sequence:<br>
- Activate ONU<br>
- Set UNI<br>
- For each traffic class<br>
	-- Set TCONT<br>
	-- Create GEM port<br>
- Create Qos Policy Profile<br>
	-- Create 802.1p Service Mapper<br>
	-- For each traffic class create GEM PORT IW TP ME<br>
	-- Set 802.1p Service Mapper<br>

**Usage**<br>
bin/test_qos_policy_profile [-h] [-a POLT_HOST] [-p POLT_PORT]
                               [-l LOGLEVEL] [-v VOMCI_NAME] [-c CTERM_NAME]
                               [-o ONU_ID] [-t TCI] [-b BACKGROUND] [-i ITERS]
                               [-d DUMP_MIB] [--timeout TIMEOUT]
                               [--retries RETRIES]
                               [--profile-name PROFILE_NAME]
                               [--uni-name UNI_NAME] [--uni-id UNI_ID]
                               [--tcont-name TCONT_NAME] [--alloc-id ALLOC_ID]
                               [--gemport-name GEMPORT_NAME]
                               [--gemport-id GEMPORT_ID]
                               [--num_pbits_per_tc NUM_PBITS_PER_TC]
                               [--num_tcs NUM_TCS] [--encryption ENCRYPTION]

**Extra Optional Parameters:**<br>
  --profile-name PROFILE_NAME; QoS policy profile name: 'qos_profile.1'<br>
  --uni-name UNI_NAME   UNI name: 'uni.1'<br>
  --uni-id UNI_ID       UNI id: 0<br>
  --tcont-name TCONT_NAME; TCONT base name: 'tcont'<br>
  --alloc-id ALLOC_ID   Base ALLOC Id: 1024<br>
  --gemport-name GEMPORT_NAME;  GEM port base name: 'gem'<br>
  --gemport-id GEMPORT_ID; GEMPORT Id: 1025<br>
  --num_pbits_per_tc NUM_PBITS_PER_TC; Number of PBIts that map to the same Traffic Class: 2<br>
  --num_tcs NUM_TCS     Number of Traffic Classes: 2<br>
  --encryption ENCRYPTION; GEM port encryption: 'NO_ENCRYPTION'<br>

### bin.test_vlan_subinterface: Create a VLAN Sub-Interface

This test performs the following sequence:<br>
- Activate ONU<br>
- Set UNI<br>
- For each traffic class<br>
	-- Set TCONT<br>
	-- Create GEM port<br>
- Create Qos Policy Profile<br>
	-- Create 802.1p Service Mapper<br>
	-- For each traffic class create GEM PORT IW TP ME<br>
	-- Set 802.1p Service Mapper<br>
- Create VLAN Tagging Filter ME<br>
- Create EXT VLAN Tag Operation ME<br>

**Usage**<br>
bin/test_vlan_subinterface [-h] [-a POLT_HOST] [-p POLT_PORT] [-l LOGLEVEL]
                              [-v VOMCI_NAME] [-c CTERM_NAME] [-o ONU_ID]
                              [-t TCI] [-b BACKGROUND] [-i ITERS]
                              [-d DUMP_MIB] [--timeout TIMEOUT]
                              [--retries RETRIES] [--subif-name SUBIF_NAME]
                              [--ingress-o-vid INGRESS_O_VID]
                              [--ingress-o-pbit INGRESS_O_PBIT]
                              [--ingress-i-vid INGRESS_I_VID]
                              [--ingress-i-pbit INGRESS_I_PBIT]
                              [--egress-o-vid EGRESS_O_VID]
                              [--egress-o-pbit EGRESS_O_PBIT]
                              [--vlan-action VLAN_ACTION]
                              [--profile-name PROFILE_NAME]
                              [--uni-name UNI_NAME] [--uni-id UNI_ID]
                              [--tcont-name TCONT_NAME] [--alloc-id ALLOC_ID]
                              [--gemport-name GEMPORT_NAME]
                              [--gemport-id GEMPORT_ID]
                              [--num_pbits_per_tc NUM_PBITS_PER_TC]
                              [--num_tcs NUM_TCS] [--encryption ENCRYPTION]

**Extra Optional Parameters:**<br>
  --subif-name SUBIF_NAME; VLAN Sub-interface name: 'vlan-subif.1'<br>
  --ingress-o-vid INGRESS_O_VID; Ingress O-VID. -1=untagged: -1<br>
  --ingress-o-pbit INGRESS_O_PBIT; Ingress O-PBIT. -1=any: -1<br>
  --ingress-i-vid INGRESS_I_VID; Ingress I-VID. -1=not used: -1<br>
  --ingress-i-pbit INGRESS_I_PBIT; Ingress I-PBIT. -1=any: -1<br>
  --egress-o-vid EGRESS_O_VID; Egress VID. : 100<br>
  --egress-o-pbit EGRESS_O_PBIT; Egress PBIT. : 0<br>
  --vlan-action VLAN_ACTION; VLAN Action (PUSH, POP, TRANSLATE). : 'PUSH'<br>
  --profile-name PROFILE_NAME; QoS policy profile name: 'qos_profile.1'<br>
  --uni-name UNI_NAME   UNI name: 'uni.1'<br>
  --uni-id UNI_ID       UNI id: 0<br>
  --tcont-name TCONT_NAME; TCONT base name: 'tcont'<br>
  --alloc-id ALLOC_ID   Base ALLOC Id: 1024<br>
  --gemport-name GEMPORT_NAME;  GEM port base name: 'gem'<br>
  --gemport-id GEMPORT_ID; GEMPORT Id: 1025<br>
  --num_pbits_per_tc NUM_PBITS_PER_TC; Number of PBIts that map to the same Traffic Class: 2<br>
  --num_tcs NUM_TCS     Number of Traffic Classes: 2<br>
  --encryption ENCRYPTION; GEM port encryption: 'NO_ENCRYPTION'<br>
