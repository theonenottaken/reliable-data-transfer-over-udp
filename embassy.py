# Caleb Shere 2-49327691-9 #

import socket
import sys
import struct

QUEUE_SIZE = 10
packet_queue = QUEUE_SIZE * [None]
ALL_DONE = 255
homeland_port = -1

# establish connection with Homeland
def establish_conn(sock):
	while True:
		data, addr = sock.recvfrom(10)
		homeland_port = addr[1]
		if data == "Hello":
			sock.sendto("hello", (host, homeland_port))
			return

# determine if the data sent from Homeland is corrupted
def is_data_corrupt(data, seq, check):
	summ = 0
	for i in range(len(data)):
		num = ord(data[i])
		summ += num
	summ += seq
	summ = summ % 256
	if ((summ + check) % 256) != 0:
		return True
	return False 

port = 10000
host = sys.argv[1]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 10000))
#sock.recvfrom(10)
establish_conn(sock)
fout = open("output.txt", "wb", 500)
finished = False
base = 0
last_num = 5000								# so base will never be greater than it except at the end
while True:
	msg, addr = sock.recvfrom(493)
	print msg
	data, sender_num, check, last = struct.unpack("%dsBB?" % (len(msg) - 3,), msg)
	corrupt = is_data_corrupt(data, sender_num, check)
	# to make ACK, data must be not corrupt and within the window. A number received outside of the window is ignored.
	if not corrupt and sender_num < (base + QUEUE_SIZE):
		ack = struct.pack('BB', sender_num, sender_num)
		# if sequence number is within the window, we must update our window
		if sender_num >= base:
			if packet_queue[sender_num - base] is None:
				packet_queue[sender_num - base] = data
				# if we've received the base packet, print it to file plus any consecutive later packets
				if sender_num == base:
					i = 0
					while packet_queue[0] is not None:
						fout.write(packet_queue[0])
						del packet_queue[0]
						packet_queue.append(None)
						i = i + 1
					# increment the base for how many packets were printed
					base += i
		sock.sendto(ack, (host, port))
	if last:
		last_num = sender_num
	if base > last_num:
		break

# in case the last ack or two was lost, homeland needs to know to terminate its execution
confirm_end = struct.pack('BB', ALL_DONE, ALL_DONE)
for i in range(5):
	sock.sendto(confirm_end, (host, relay_port))

fout.close()
sock.close()