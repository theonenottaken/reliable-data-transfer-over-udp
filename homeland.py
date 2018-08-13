# Caleb Shere 2-49327691-9 #

import socket
import sys
import time
import struct

QUEUE_SIZE = 10
packet_queue = QUEUE_SIZE * [None]
SOCK_TIME = 3.0
TO_READ = 490
seq_num = 0
base = 0
PACKET = 0
SEQ_NUM = 1
TIME = 2
ALL_DONE = 255

# establishes connection with the embassy
def establish_conn(sock):
	while True:
		sock.sendto("Hello", (host, embassy_port))
		data, addr = sock.recvfrom(10)
		if data == "hello":
			return

# generates and returns a checksum for the given string and number
def get_check(s, num):
	check_sum = 0
	for c in s:
		n = ord(c)
		check_sum += n
	check_sum += num
	check_sum = (256 - (check_sum % 256)) % 256
	return check_sum

# Gets n packets to send to Embassy
def get_packets(n):
	pack_list = []
	done = False
	global seq_num
	for i in range(n):
		# read a chunk of text from the file
		text = fin.read(TO_READ)
		if len(text) < TO_READ:
			done = True
		# create checksum
		check = get_check(text, seq_num)
		# send to Embassy the length of the text, the text, sequence number, checksum, and whether or not this is the last packet
		packet = struct.pack("%dsBB?" % (len(text),), text, seq_num, check, done)
		pack_list.append((packet, seq_num))
		if done:
			break
		seq_num = seq_num + 1
	return (pack_list, done)

# Receive any ACKs that have been sent by Embassy
def receive_acks():
	try:
		msg, addr = sock.recvfrom(2 * QUEUE_SIZE)
	# if timeout with no received ACK, assume packets were lost and resend packets in queue
	except socket.timeout:
		for pTup in packet_queue:
			if pTup is not None:
				print pTup[PACKET]
				sock.sendto(pTup[PACKET], (host, embassy_port))
				# record the time of sending this packet
				pTup[TIME] = time.clock()
		# call this function again now that we have resent packets
		return receive_acks()
	else:
		global base
		ack_pairs = []
		# every ACK consists of two bytes
		num_acks = len(msg) / 2
		index = 0
		move_base = 0
		for i in range(num_acks):
			next_pair = msg[index:index + 2]
			ack1, ack2 = struct.unpack('BB', next_pair)
			if ack1 == ack2:
				if ack1 == ALL_DONE:
					# clear the queue
					for i in range(QUEUE_SIZE):
						packet_queue[i] = None
					return 0
				# find the packet that has been acknowledged
				ind = find_pack(ack1)
				if ind is not None:
					packet_queue[ind] = None
				# if base packet has been acknowledged, update base, move window
				if ack1 == base:
					i = 0
					while packet_queue[0] is None and i < QUEUE_SIZE:
						del packet_queue[0]
						packet_queue.append(None)
						i = i + 1
					move_base += i
			# this is the index of the message received from Embassy. In other words, move to next ACK.
			index += 2
		base += move_base
		return move_base

# check for packets that have timed out (not received an ACK in time SOCK_TIME) and resend accordingly
def resend_timedout_packs():
	for p in packet_queue:
		if p is not None:
			t = time.clock()
			elapsed = t - p[TIME]
			if elapsed > SOCK_TIME:
				print p[PACKET]
				socket.sendto(p[PACKET], (host, embassy_port))
				p[TIME] = time.clock()

# send all packets from given list pack_list, resend timed out packets, and return how many more packets to retrieve from file
def send_packets(pack_list):
	for p in pack_list:
		packet = p[PACKET]
		num = p[SEQ_NUM]
		print packet
		sock.sendto(packet, (host, embassy_port))
		packet_queue[num - base] = ([packet, num, time.clock()])
	resend_timedout_packs()
	get_more = receive_acks()
	return get_more

# find the packet corresponding to the given sequence number
def find_pack(num):
	i = 0
	for p in packet_queue:
		if p is not None and p[SEQ_NUM] == num:
			return i
		i = i + 1
	return None

# determine if the packet queue is empty, which for our purposes means that every index is None
def is_empty(pQueue):
	for p in pQueue:
		if p is not None:
			return False
	return True

embassy_port = 10000
host = sys.argv[1]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# establish connection with Embassy - now Embassy will know Homeland's port number
establish_conn(sock)
sock.settimeout(SOCK_TIME)

fin = open("input.txt", "rb", 500)
finished = False
to_get = QUEUE_SIZE
while not finished:
	pack_list, finished = get_packets(to_get)
	to_get = send_packets(pack_list)
while not is_empty(packet_queue):
	receive_acks()

fin.close()
sock.close()