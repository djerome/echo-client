#!local/bin/python
#
# File: echo_client.py
#
#	Sends and receives message to/from echo_server
#

import time
import socket
import sys
import os
import logging
from logging.handlers import TimedRotatingFileHandler

# Initializations
sleep_time = 5
test_period = 60
server_host = 'cranberry'
server_port = 10000
num_tries = 5
message_sent = socket.gethostname()
receive_chunk = 16

# logging constants
log_file = "/var/log/conn_test/conn_test.log"
log_format = "%(asctime)s: %(message)s"
date_format = "%m/%d/%Y %X"

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create timed rotating file handler and set level to debug
fh = TimedRotatingFileHandler(log_file, when='D', interval=30, backupCount=12)
fh.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

# add formatter to file handler
fh.setFormatter(formatter)

# add file handler to logger
logger.addHandler(fh)

# log program restart
logger.info('RESTART: ' + os.path.basename(__file__))

while True:

	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = (server_host, server_port)
	print('Trying to connect to {} port {}'.format(*server_address))

	# Try num_tries times to connect to server
	connect_OK = False
	for i in range(num_tries):
		print 'Try # ' + str(i)
		try:
			sock.connect(server_address)
			connect_OK = True
			break

		except IOError as e:
			print "I/O error({0}): {1}".format(e.errno, e.strerror)
			print "Unable to connect"
			part1 = 'Unable to connect to {}, port {}'.format(*server_address)
			part2 = '; I/O error({0}): {1}'.format(e.errno, e.strerror)
			error_msg = part1 + part2
			logger.info(error_msg)
			time.sleep(sleep_time)

	if connect_OK:
		print "Connection OK, trying to send data"

		send_OK = False
		for i in range(num_tries):
			print 'Try # ' + str(i)
			try:

				# Send message
				sock.sendall(message_sent)
				send_OK = True
				break

			except IOError as e:
				print "I/O error({0}): {1}".format(e.errno, e.strerror)
				print "Unable to send"
				part1 = 'Unable to send data to {}, port {}'.format(*server_address)
				part2 = '; I/O error({0}): {1}'.format(e.errno, e.strerror)
				error_msg = part1 + part2
				logger.info(error_msg)
				time.sleep(sleep_time)

		if send_OK:
			print "Data Sent OK, trying to receive data"

			receive_OK = False
			for i in range(num_tries):
				print 'Try # ' + str(i)
				amount_received = 0
				amount_expected = len(message_sent)
				message_recd = ''

				try:
					# Look for the response
					while amount_received < amount_expected:
						data = sock.recv(receive_chunk)
						message_recd += data
						amount_received += len(data)
						print 'Received: ' + data

					if not(cmp(message_sent, message_recd)):
						receive_OK = True
						print 'Received OK'
					else:
						logger.info('INCOMPLETE message received')
					break

				except IOError as e:
					print "I/O error({0}): {1}".format(e.errno, e.strerror)
					print "Unable to receive"
					part1 = 'Unable to receive data from {}, port {}'.format(*server_address)
					part2 = '; I/O error({0}): {1}'.format(e.errno, e.strerror)
					error_msg = part1 + part2
					logger.info(error_msg)
					time.sleep(sleep_time)

		else:
			print "Data NOT Sent OK, not receiving data"

	else:
		print "Connection NOT OK, not sending data"

	print('closing socket')
	sock.close()
	time.sleep(test_period)
