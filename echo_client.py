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
sleep_time = 3
server_host = 'raspberry'
server_port = 10000
num_tries = 5

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

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (server_host, server_port)
print('connecting to {} port {}'.format(*server_address))

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
else:
	print "Connection NOT OK, not sending data"

if connect_OK:

	send_OK = False
	for i in range(num_tries):
		print 'Try # ' + str(i)
		try:

			# Send hostname as message
			message_sent = socket.gethostname()
			print 'Sending: ' + message_sent
			logger.info('Sending message to ' + str(server_address))
			sock.sendall(message_sent)
			send_OK = True
			break

		except IOError as e:
			print "I/O error({0}): {1}".format(e.errno, e.strerror)
			print "Unable to send"
			time.sleep(sleep_time)

	if send_OK:
		print "Data Sent OK, trying to receive data"
	else:
		print "Data NOT Sent OK, not receiving data"

if connect_OK and send_OK:

	receive_OK = False
	for i in range(num_tries):
		print 'Try # ' + str(i)
		try:

			# Look for the response
			amount_received = 0
			amount_expected = len(message_sent)
			message_recd = ''

			while amount_received < amount_expected:
				data = sock.recv(16)
				message_recd += data
				amount_received += len(data)
				print 'Received: ' + data

			print 'Complete msg received = ' + message_recd
			if not(cmp(message_sent, message_recd)):
				logger.info('Complete message received')
			else:
				logger.info('INCOMPLETE message received')
			break

		except IOError as e:
			print "I/O error({0}): {1}".format(e.errno, e.strerror)
			print "Unable to receive"
			time.sleep(sleep_time)

logger.info('closing socket')
print('closing socket')
sock.close()
