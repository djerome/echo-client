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
# number of tries and time between tries in a single attempt
try_sleep_time = 1
num_tries = 5
# number of attempts and time between attempts before restarting network interface
attempt_sleep_time = 15
num_attempts = 3
# host and port where echo server is running
host = 'cranberry'
port = 10000
server_address = (host, port)
# message to be echo'd between the client and server
message_sent = socket.gethostname()
# number of bytes to receive from server in a single chunk
receive_chunk = 16

# Setup Logging
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

# Main loop
while True:

	# attempt num_attempts before restarting interface
	interface_OK = False
	for i in range(num_attempts):
		print 'Attempt # ' + str(i)

		# Create a TCP/IP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect the socket to the port where the server is listening
		print('Trying to connect to {} port {} ...'.format(*server_address))

		# Try num_tries times to connect to server
		connect_OK = False
		for j in range(num_tries):
			print 'Try # ' + str(j)
			try:
				# connect to server
				sock.connect(server_address)
				connect_OK = True
				print "Connection OK"
				# break out of connect loop
				break

			except IOError as e:
				error_msg = 'Unable to connect to {0}, port {1}; I/O error({2}): {3}'.format(host, port, e.errno, e.strerror)
				logger.info(error_msg)
				print(error_msg)
				time.sleep(try_sleep_time)

		# end of connect loop
		if connect_OK:
			print "Trying to send data ..."

			# Try num_tries times to send message to server
			send_OK = False
			for j in range(num_tries):
				print 'Try # ' + str(j)
				try:
					# send message
					sock.sendall(message_sent)
					send_OK = True
					print "Data sent OK"
					# break out of send loop
					break

				except IOError as e:
					error_msg = 'Unable to send data to {0}, port {1}; I/O error({2}): {3}'.format(host, port, e.errno, e.strerror)
					logger.info(error_msg)
					print(error_msg)
					time.sleep(try_sleep_time)

			# end of send loop
			if send_OK:
				print "Trying to receive data ..."

				# Try num_tries times to receive message from server
				receive_OK = False
				for j in range(num_tries):
					print 'Try # ' + str(j)
					amount_received = 0
					amount_expected = len(message_sent)
					message_recd = ''

					try:
						# receive message - look for the response and continue receiving data until finished
						while amount_received < amount_expected:
							data = sock.recv(receive_chunk)
							message_recd += data
							amount_received += len(data)
							print 'Received: ' + data

						# Also check if message received is same as message sent
						if not(cmp(message_sent, message_recd)):
							receive_OK = True
							print "Data received OK"
							# break out of receive loop
							break
						else:
							print 'Data Received is different from data sent'
							logger.info('INCOMPLETE message received')

					except IOError as e:
						error_msg = 'Unable to receive data from {0}, port {1}; I/O error({2}): {3}'.format(host, port, e.errno, e.strerror)
						logger.info(error_msg)
						print(error_msg)
						time.sleep(try_sleep_time)

				# end of receive loop
				if receive_OK:
					interface_OK = True
					# break out of attempt loop
					break
				else:
					print "Data NOT received OK"

			else:
				print "Data NOT Sent OK, not receiving data"

		else:
			print "Connection NOT OK, not sending data"

		# cleanup and sleep before next attempt
		print('Closing socket\n')
		sock.close()
		time.sleep(attempt_sleep_time)

	# end of attempt loop
	if interface_OK:
		# cleanup and sleep before starting attempts again
		print "Interface OK"
		print('Closing socket\n')
		sock.close()
		time.sleep(attempt_sleep_time)
	else:
		print "Restarting Interface\n"
		logger.info('Restarting Network Interface')
