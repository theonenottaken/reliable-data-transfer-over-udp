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

def establish_conn(sock):
	while True:
		sock.sendto("Hello", (host, relay_port))
		data, addr = sock.recvfrom(10)
		if data == "hello":
			return

def get_check(s, num):
	check_sum = 0
	for c in s:
		n = ord(c)
		check_sum += n
	check_sum += num
	check_sum = (256 - (check_sum % 256)) % 256
	return check_sum

def get_packets(n):
	pack_list = []
	done = False
	global seq_num
	for i in range(n):
		st = fin.read(TO_READ)
		if len(st) < TO_READ:
			done = True
		check = get_check(st, seq_num)
		packet = struct.pack("%dsBB?" % (len(st),), st, seq_num, check, done)
		pack_list.append((packet, seq_num))
		if done:
			break
		seq_num = seq_num + 1
	return (pack_list, done)

def receive_acks():
	try:
		msg, addr = sock.recvfrom(2 * QUEUE_SIZE)
	except socket.timeout:
		for pTup in packet_queue:
			if pTup is not None:
				sock.sendto(pTup[0], (host, relay_port))
				pTup[2] = time.clock()
		return receive_acks()
	else:
		global base
		ack_pairs = []
		num_acks = len(msg) / 2
		index = 0
		for i in range(num_acks):
			next_pair = msg[index:index + 2]
			ack1, ack2 = struct.unpack('BB', next_pair)
			if ack1 == ack2:
				if ack1 == 255:
					for i in range(QUEUE_SIZE):
						packet_queue[i] = None
					return 0
				ind = find_pack(ack1)
				if ind is not None:
					packet_queue[ind] = None
				move_base = 0
				if ack1 == base:
					i = 0
					while packet_queue[0] is None and i < QUEUE_SIZE:
						del packet_queue[0]
						packet_queue.append(None)
						i = i + 1
					move_base += i
			index += 2
		base += move_base
		return move_base

def resend_timedout_packs():
	for p in packet_queue:
		if p is not None:
			t = time.clock()
			elapsed = t - p[2]
			if elapsed > SOCK_TIME:
				socket.sendto(p[0], (host, relay_port))
				p[2] = time.clock()

def send_packets(pack_list):
	for p in pack_list:
		packet = p[0]
		num = p[1]
		sock.sendto(packet, (host, relay_port))
		packet_queue[num - base] = ([packet, num, time.clock()])
	resend_timedout_packs()
	get_more = receive_acks()
	return get_more

def find_pack(num):
	i = 0
	for p in packet_queue:
		if p is not None and p[1] == num:
			return i
		i = i + 1
	return None

def is_empty(pQueue):
	for p in pQueue:
		if p is not None:
			return False
	return True

relay_port = 10000
host = sys.argv[1]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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