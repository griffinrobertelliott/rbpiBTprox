import fcntl
import struct
import array
import bluetooth
import bluetooth._bluetooth as bt
import time
import os
import datetime
import requests


def bluetooth_rssi(addr):
    # Open hci socket
    hci_sock = bt.hci_open_dev()
    hci_fd = hci_sock.fileno()

    # Connect to device 
    bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
##    bt_sock.settimeout(10)
    result = bt_sock.connect_ex((addr, 1))	# PSM 1 - Service Discovery

    try:
        # this is getting the connection info
        reqstr = struct.pack("6sB17s", bt.str2ba(addr), bt.ACL_LINK, "\0" * 17)
        request = array.array("c", reqstr )
        handle = fcntl.ioctl(hci_fd, bt.HCIGETCONNINFO, request, 1)
        handle = struct.unpack("8xH14x", request.tostring())[0]

        # this is getting the RSSI information
        cmd_pkt=struct.pack('H', handle)
        rssi = bt.hci_send_req(hci_sock, bt.OGF_STATUS_PARAM,
                     bt.OCF_READ_RSSI, bt.EVT_CMD_COMPLETE, 4, cmd_pkt)
        rssi = struct.unpack('b', rssi[3])[0]

        # this is closing the sockets
        bt_sock.close()
        hci_sock.close()

        return rssi

    except:
        return None



far = True
far_count = 0
near_count = 0

# assume that the phone is not in range yet:
rssi = -255
rssi_prev1 = -255
rssi_prev2 = -255

phone_addr = 'E4:2B:34:4F:A8:10'

debug = 1

while True:
    # get rssi reading for address
    rssi = bluetooth_rssi(phone_addr)

    if debug:
        print datetime.datetime.now(), rssi, near_count, far, far_count #far ##rssi_prev1, rssi_prev2, far_count


    if rssi == rssi_prev1 == rssi_prev2 == None:
        print datetime.datetime.now(), "can't detect address"
        time.sleep(0)

    elif rssi > -10: # and rssi_prev1 > -35 and rssi_prev2 > -40:
        # change state if nearby
        #if far:
        near_count += 1
        far_count = 0
        if far and near_count >= 50:
            far = False
            if near_count == 50:
                #resp = requests.get('https://sonos-flow.now.sh/flow/enter/Downstairs/CNN (US News)')
                resp = requests.get('http://Brandens-Macbook-Pro-2.local:5000/flow/enter/Downstairs')
                print 'Made the call!'
                print 'Status Code: %i' % resp.status_code
            
            ##code here to ENTER sonos webserver
			
	    
            time.sleep(0.5)
            
    elif rssi < -10 and near_count < 25:
        near_count = 0
            

    elif rssi < -13: #and rssi_prev1 < -40 and rssi_prev2 < -40:
        # if were near and single has been consisitenly low

        # need 10 (might want to change this to be higher for our app. count of 10 is relatively low, meaning super short time, like 5 seconds) in a row to set to far
        far_count += 1
        if not far and far_count >= 50: ##trying count of 100 for sonos application
            # switch state to far
            far = True
            near_count = 0
            #resp = requests.get('http://192.168.86.96:5000/flow/exit/Downstairs')
            if far_count == 50:
                #resp = requests.get('https://sonos-flow.now.sh/flow/exit/Downstairs')
                resp = requests.get('http://Brandens-Macbook-Pro-2.local:5000/flow/exit/Downstairs')
                print 'Made the call!'
                print 'Status Code: %i' % resp.status_code
            far_count = 0
            
            time.sleep(0.5)

    else:
        far_count = 0


    rssi = rssi_prev1
    rssi_prev1  = rssi_prev2
