import fcntl
import struct
import array
import bluetooth
import bluetooth._bluetooth as bt
import time
import os
import datetime

def bluetooth_rssi(addr):
    # Open hci socket
    hci_sock = bt.hci_open_dev()
    hci_fd = hci_sock.fileno()

    # Connect to device 
    bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
##    bt_sock.settimeout(10)
    result = bt_sock.connect_ex((addr, 1))	# PSM 1 - Service Discovery

    try:
        # Get ConnInfo
        reqstr = struct.pack("6sB17s", bt.str2ba(addr), bt.ACL_LINK, "\0" * 17)
        request = array.array("c", reqstr )
        handle = fcntl.ioctl(hci_fd, bt.HCIGETCONNINFO, request, 1)
        handle = struct.unpack("8xH14x", request.tostring())[0]

        # Get RSSI
        cmd_pkt=struct.pack('H', handle)
        rssi = bt.hci_send_req(hci_sock, bt.OGF_STATUS_PARAM,
                     bt.OCF_READ_RSSI, bt.EVT_CMD_COMPLETE, 4, cmd_pkt)
        rssi = struct.unpack('b', rssi[3])[0]

        # Close sockets
        bt_sock.close()
        hci_sock.close()

        return rssi

    except:
        return None



far = True
far_count = 0

# assume phone is initially far away
rssi = -255
rssi_prev1 = -255
rssi_prev2 = -255

near_cmd = 'br -n 1'
far_cmd = 'br -f 1'

phone_addr = '00:17:53:9E:80:D2'

debug = 1

while True:
    # get rssi reading for address
    rssi = bluetooth_rssi(phone_addr)

    if debug:
        print datetime.datetime.now(), rssi, far ##rssi_prev1, rssi_prev2, far_count


    if rssi == rssi_prev1 == rssi_prev2 == None:
        print datetime.datetime.now(), "can't detect address"
        time.sleep(0)

    elif rssi < -30 and rssi_prev1 < -30 and rssi_prev2 < -30:
        # change state if nearby
        #if far:
            far = False
            far_count = 0
            os.system(near_cmd)
            
            ##code here to ENTER sonos webserver
			
	    
            time.sleep(1)

    elif rssi < -40 and rssi_prev1 < -40 and rssi_prev2 < -40:
        # if were near and single has been consisitenly low

        # need 10 (might want to change this to be higher for our app. count of 10 is relatively low, meaning super short time, like 5 seconds) in a row to set to far
        far_count += 1
        if not far and far_count > 100: ##trying count of 100 for sonos application
            # switch state to far
            far = True
            far_count = 0
            os.system(far_cmd)
            
            ##code here to EXIT sonos webserver
	    
            time.sleep(1)

    else:
        far_count = 0


    rssi = rssi_prev1
    rssi_prev1  = rssi_prev2
