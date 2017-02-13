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
import subprocess

# Initializations
# number of tries and time between tries in a single attempt
try_sleep_time = 5
max_tries = 5
# number of attempts and time between attempts before restarting network interface
attempt_sleep_time = 15
max_attempts = 3
# wait time between tests
wait_time = 120
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

	# attempt max_attempts before restarting interface
	interface_OK = False
	for i in range(max_attempts):

		# Create a TCP/IP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Try max_tries times to connect to server
		connect_OK = False
		for j in range(max_tries):
			try:
				# connect to server
				sock.connect(server_address)
				connect_OK = True
				# break out of connect loop
				break

			except IOError as e:
				error_msg = 'Unable to connect to {0}:{1}; I/O error({2}): {3}'.format(host, port, e.errno, e.strerror)
				logger.info(error_msg)
				time.sleep(try_sleep_time)

		# end of connect loop
		if connect_OK:

			# Try max_tries times to send message to server
			send_OK = False
			for j in range(max_tries):
				try:
					# send message
					sock.sendall(message_sent)
					send_OK = True
					# break out of send loop
					break

				except IOError as e:
					error_msg = 'Unable to send data to {0}:{1}; I/O error({2}): {3}'.format(host, port, e.errno, e.strerror)
					logger.info(error_msg)
					time.sleep(try_sleep_time)

			# end of send loop
			if send_OK:

				# Try max_tries times to receive message from server
				receive_OK = False
				for j in range(max_tries):
					amount_received = 0
					amount_expected = len(message_sent)
					message_recd = ''

					try:
						# receive message - look for the response and continue receiving data until finished
						while amount_received < amount_expected:
							data = sock.recv(receive_chunk)
							message_recd += data
							amount_received += len(data)

						# Also check if message received is same as message sent
						if not(cmp(message_sent, message_recd)):
							receive_OK = True
							# break out of receive loop
							break
						else:
							logger.info('INCOMPLETE message received')

					except IOError as e:
						error_msg = 'Unable to receive data from {0}:{1}; I/O error({2}): {3}'.format(host, port, e.errno, e.strerror)
						logger.info(error_msg)
						time.sleep(try_sleep_time)

				# end of receive loop
				sock.close()
				if receive_OK:
					interface_OK = True
					# break out of attempt loop
					break

		# sleep between attmpts
		time.sleep(attempt_sleep_time)

	# end of attempt loop

	# if interface is not OK after all attempts, restart it
	if not(interface_OK):
		logger.info('Restarting Network Interface')
		subprocess.call(['/sbin/ifdown wlan0 && sleep 10 && /sbin/ifup --force wlan0'], shell=True)
	else:
		log_msg = 'Connected OK to ' + host + ':' + str(port)
		logger.info(log_msg)

	# sleep before trying test again
	time.sleep(wait_time)
