## Sample gpb-messages that can be used in producer ##

#=================== CREATE_ONU=========================
#OK_RESPONSE:

msg.header.msg_id="1"
msg.header.sender_name="vomci1"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_FUNCTION
msg.header.object_name="vomci1"

msg.body.response.rpc_resp.status_resp.status_code=0


msg.header.msg_id="2"
msg.header.sender_name="vomci-proxy"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_PROXY
msg.header.object_name="vomci-proxy"

msg.body.response.rpc_resp.status_resp.status_code=0

#ERROR-RESPONSE:

msg.header.msg_id="1"
msg.header.sender_name="vomci1"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_FUNCTION
msg.header.object_name="vomci1"

msg.body.response.rpc_resp.status_resp.status_code=1
error.error_type = "application"
error.error_tag="invalid-value"
error.error_severity="major"
error.error_app_tag="vomci-app"
error.error_path="/bbf-vomci-func:create-onu"
error.error_message="op failed"
msg.body.response.rpc_resp.status_resp.error.append(error)


msg.header.msg_id="2"
msg.header.sender_name="vomci-proxy"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_PROXY
msg.header.object_name="vomci-proxy"

msg.body.response.rpc_resp.status_resp.status_code=1
error.error_type = "application"
error.error_tag="invalid-value"
error.error_severity="major"
error.error_app_tag="vproxy-app"
error.error_path="/bbf-vomci-proxy:create-onu"
error.error_message="op failed"
msg.body.response.rpc_resp.status_resp.error.append(error)


#=================== SET_ONU_COMM ======
##OK_RESPONSE:

msg.header.msg_id="3"
msg.header.sender_name="vomci1"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_FUNCTION
msg.header.object_name="vomci1"

msg.body.response.action_resp.status_resp.status_code=0

msg.header.msg_id="4"
msg.header.sender_name="vomci-proxy"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_PROXY
msg.header.object_name="vomci-proxy"

msg.body.response.action_resp.status_resp.status_code=0

## ERROR_RESPONSE:

msg.header.msg_id="3"
msg.header.sender_name="vomci1"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_FUNCTION
msg.header.object_name="vomci1"

msg.body.response.action_resp.status_resp.status_code=1
error.error_type = "application"
error.error_tag="invalid-value"
error.error_severity="major"
error.error_app_tag="vomci-app"
error.error_path="/bbf-vomci-func:set-onu-communication"
error.error_message="internal error"
msg.body.response.action_resp.status_resp.error.append(error)


msg.header.msg_id="4"
msg.header.sender_name="vomci-proxy"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_PROXY
msg.header.object_name="vomci-proxy"

msg.body.response.action_resp.status_resp.status_code=1

error.error_type = "application"
error.error_tag="invalid-value"
error.error_severity="major"
error.error_app_tag="vproxy-app"
error.error_path="/bbf-vomci-proxy:set-onu-communication"
error.error_message="internal error"
msg.body.response.action_resp.status_resp.error.append(error)

#=================== DELETE_ONU ======

##OK_RESPONSE:

msg.header.msg_id="5"
msg.header.sender_name="vomci1"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_FUNCTION
msg.header.object_name="vomci1"

msg.body.response.action_resp.status_resp.status_code=0


msg.header.msg_id="6"
msg.header.sender_name="vomci-proxy"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_PROXY
msg.header.object_name="vomci-proxy"

msg.body.response.action_resp.status_resp.status_code=0


## ERROR_RESPONSE:

msg.header.msg_id="3"
msg.header.sender_name="vomci1"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_FUNCTION
msg.header.object_name="vomci1"

msg.body.response.action_resp.status_resp.status_code=1
error.error_type = "application"
error.error_tag="invalid-value"
error.error_severity="major"
error.error_app_tag="vomci-app"
error.error_path="/bbf-vomci-func:delete-onu"
error.error_message="internal error"
msg.body.response.action_resp.status_resp.error.append(error)


msg.header.msg_id="4"
msg.header.sender_name="vomci-proxy"
msg.header.recipient_name="vOLTMF"
msg.header.object_type=msg.header.VOMCI_PROXY
msg.header.object_name="vomci-proxy"

msg.body.response.action_resp.status_resp.status_code=1

error.error_type = "application"
error.error_tag="invalid-value"
error.error_severity="major"
error.error_app_tag="vproxy-app"
error.error_path="/bbf-vomci-proxy:delete-onu"
error.error_message="internal error"
msg.body.response.action_resp.status_resp.error.append(error)
