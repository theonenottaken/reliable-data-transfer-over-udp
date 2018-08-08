# Caleb Shere 2-49327691-9 #

import socket
import sys
import struct

QUEUE_SIZE = 10
packet_queue = QUEUE_SIZE * [None]

def establish_conn(sock):
	while True:
		sock.sendto("Hello", (host, relay_port))
		data, addr = sock.recvfrom(10)
		if data == "hello":
			return

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

relay_port = 10000
host = sys.argv[1]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
establish_conn(sock)
fout = open("output.txt", "wb", 500)
finished = False
base = 0
last_num = 5000								# so base will never be greater than it except at the end
while True:
	msg, addr = sock.recvfrom(493)
	data, sender_num, check, last = struct.unpack("%dsBB?" % (len(msg) - 3,), msg)
	corrupt = is_data_corrupt(data, sender_num, check)
	if not corrupt and sender_num < (base + QUEUE_SIZE):
		ack = struct.pack('BB', sender_num, sender_num)
		if sender_num >= base:
			if packet_queue[sender_num - base] is None:
				packet_queue[sender_num - base] = data
				if sender_num == base:
					i = 0
					while packet_queue[0] is not None:
						fout.write(packet_queue[0])
						del packet_queue[0]
						packet_queue.append(None)
						i = i + 1
					base += i
		sock.sendto(ack, (host, relay_port))
	if last:
		last_num = sender_num
	if base > last_num:
		break

# in case the last ack or two was lost, homeland needs to know to terminate its excecution
confirm_end = struct.pack('BB', 255, 255)
for i in range(5):
	sock.sendto(confirm_end, (host, relay_port))

fout.close()
sock.close()