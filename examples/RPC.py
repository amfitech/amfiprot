import sys
sys.path.append("..")
import amfiprot
import amfiprot_amfitrack as amfitrack
import struct
import easygui
import numpy
import math
import re

VENDOR_ID = 0xC17
PRODUCT_ID = 0xD12
# PRODUCT_ID = 0xD01

rpc_spec_pattern = r"<ReplyProcedureSpec> RPC_Index: (\d+), RPC_UID: (\d+), RPC_ReturnValueType: (\d+), RPC_Param1Type: (\d+), RPC_Param2Type: (\d+), RPC_Param3Type: (\d+), RPC_Param4Type: (\d+), RPC_Param5Type: (\d+)"


if __name__ == "__main__":
    conn = amfiprot.USBConnection(VENDOR_ID, PRODUCT_ID)
    print(conn)
    nodes = conn.find_nodes()
    print(nodes)

    Devs = []
    if len(nodes) > 1:
        lindex = easygui.multchoicebox("select Devices", "title", [node for node in nodes])
        print(lindex)
        for Node in nodes:
            if str(Node) in lindex:
                Devs.append(amfitrack.Device(Node))
                print("Node init as device")
    else:
        Devs.append(amfitrack.Device(nodes[0]))

    conn.start()

    for idx, Dev in enumerate(Devs):
        packet = Dev.getProcedureSpec(0, 0)
        rpc_spec_match = re.search(rpc_spec_pattern, str(packet))
        print(packet)
        if rpc_spec_match:
            rpc_index = int(rpc_spec_match.group(1))
            rpc_uid = int(rpc_spec_match.group(2))
            rpc_return_value_type = int(rpc_spec_match.group(3))
            rpc_param1_type = int(rpc_spec_match.group(4))
            rpc_param2_type = int(rpc_spec_match.group(5))
            rpc_param3_type = int(rpc_spec_match.group(6))
            rpc_param4_type = int(rpc_spec_match.group(7))
            rpc_param5_type = int(rpc_spec_match.group(8))
            print(rpc_uid)
            packet = Dev.callProcedure(rpc_uid, rpc_param1_type, 230)
            print(packet)


