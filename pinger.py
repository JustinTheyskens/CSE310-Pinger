import os
import sys
import struct
import time
import select
import socket
import binascii

ICMP_ECHO_REQUEST = 8
rtt_min = float('+inf')
rtt_max = float('-inf')
rtt_sum = 0
rtt_cnt = 0
list = []

def checksum(string):
    csum = 0
    countTo = (len(string) / 2) * 2

    count = 0
    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff #0xffffffffL
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(str) - 1])
        csum = csum & 0xffffffff #0xffffffffL

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    global rtt_min, rtt_max, rtt_sum, rtt_cnt
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start

        icmpHeader = recPacket[20:28]  # the header
        type, code, checksum, pID, seq = struct.unpack("bbHHh", icmpHeader)
        size = len(recPacket)  # size of packet

        if pID == ID:
            bytes = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytes])[0]
            rtt = timeReceived - timeSent
            rtt = rtt * 1000  # seconds to ms
            rtt = round(rtt, 1)

            print(f"{size} bytes from {addr[0]}; time={rtt} ms")
            list.append(rtt)
        # Fill in end

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())  # 8 bytes
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
        # Convert 16-bit integers from host to network byte order.
    else:
        myChecksum = socket.htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object


def doOnePing(destAddr, timeout):
    icmp = socket.getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details see: http://sock-raw.org/papers/sock_raw

    # Fill in start

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp) #using SOCK_RAW

    # Fill in end

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay


def ping(host, timeout=1):
    global rtt_min, rtt_max, rtt_sum, rtt_cnt
    cnt = 0
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = socket.gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    # Send ping requests to a server separated by approximately one second
    rtt_min = 100
    rtt_max = 0
    rtt_avg = 0
    try:
        while True:
            cnt += 1
            doOnePing(dest, timeout)
            time.sleep(1)
            if len(list) > 0: #find avg rtt
                n = 0
                rtt_avg = 0
                for i in list:
                    if i > rtt_max:
                        rtt_max = list[n]
                    if i < rtt_min:
                        rtt_min = list[n]

                    rtt_avg = rtt_avg + list[n]
                    n += 1
                rtt_avg = rtt_avg / len(list)
                rtt_avg = "{:.2f}".format(rtt_avg)
    except KeyboardInterrupt:
        print(f"min/avg/max rtt: {rtt_min}/{rtt_avg}/{rtt_max}")  # print avg rtt

# Fill in start

# Calculate Statistics here

# Fill in end

if __name__ == '__main__':
    #sys.argv.append("www.google.com")
    ping(sys.argv[1])