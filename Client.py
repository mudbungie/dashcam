# Library for handling transactions between client and server

import requests
import logging
from uuid import uuid4
from hashlib import sha512
from sys import argv

logging.basicConfig(level=logging.DEBUG)


# Fetches or creates username and password
def get_auth():
	try:
		with open('dash.auth') as authfile:
			auth = [l.strip() for l in authfile.readlines() if l]
			if auth:
				return auth
	except FileNotFoundError:
		pass # If it's not there, the failure case creates it.
	with open('dash.auth', 'w') as authfile:
		authfile.write(str(uuid4()) + '\n' + str(uuid4()))
		authfile.close()
		return get_auth()

def verify_server(s):
	try:
		r = requests.get(server_url)
		if r.status_code == 200:
			return True
		elif r.status_code == 401:
			return False
		else:
			logging.error(('Unexpected status code {} while attempting communication '
				'with {}'.format(r.status_code, server_url)))
			
	except requests.exceptions.RequestException:
		logging.error('Unknown error while attempting communication with {}'.\
			format(server_url))

def register(s):
	username, password = s.auth
	try:
		r = requests.post('{}/register'.format(server_url),
			data={'user':username, 'password':password})
		print(r.text)
		if r.status_code == 200:
			logging.info('Registration of user {} successful.'.format(username))
			return True
		else:
			logging.warn('Registration unsuccessful.')
			return False
	except requests.exceptions.RequestException:
		raise
		logging.error('Unknown error while registering.')

def check_for_video(s, video, video_hash):
	try:
		r = s.get('{}/hash/{}'.format(server_url, video_hash))
		logging.debug('Response for informational request regarding video {}: {}'.\
			format(video_hash, r.body))
		if r.body == 'True':
			return True
		else:
			return False
	except requests.exceptions.RequestException:
		logging.error('Unexpected error while requesting information on hash {}.'.\
			format(video_hash))

def post_video(s, video):
	try:
		logging.debug('Uploading video.')
		s.post('{}/upload'.format(server_url), files={'file':('whatever', video)})
		logging.debug('Upload complete.')
		return True
	except requests.exceptions.RequestException:
		logging.error('Unexpected error while posting video.')
		return False
	
# Main function.
def upload(video_path):
	with open(video_path, 'rb') as video_file:
		video = video_file.read()
	video_hash = sha512(video).hexdigest()
	logging.debug('Beginning transaction regarding video with hash {}'.\
		format(video_hash))

	s = requests.Session()
	s.auth = get_auth()

	try:
		if verify_server(s):
			if not check_for_video(s, video, video_hash):
				if post_video(s, video):
					logging.info('Successful upload of video with hash {}'.\
						format(video_hash))
					return True
				else:
					logging.warn('Video upload failed for video with hash {}'.\
						format(video_hash))
			else:
				logging.info('Video with hash {} already uploaded.'.format(video_hash))
		else:
			register(s)

	except requests.exceptions.HTTPError:
		#FIXME check that the error code is 401.
		logging.warn('Application not registered.')
		register(s)
		logging.info('Application has submitted registration.\n'+\
			'You must authorize the new registration on the server.')

	return False

if __name__ == '__main__':
	server_url = argv[2]
	upload(argv[1])
