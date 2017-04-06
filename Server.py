# Server side for dashcam uploads. Runs HTTP server, which accepts uploads of
# videos, and stores a local database of uploaded video hashes, which drives
# assertions of which videos exist.

from bottle import route, run, request, auth_basic
from datetime import datetime
from hashlib import sha512

from Database import db, Base

@route('/register', method='POST')
def register():
	user = request.POST['user']
	password = request.POST['password']

	# Throw out anything that isn't alphanumeric.
	if not user.isalpha() or not password.isalpha():
		return False

	password = sha512(password.encode()).hexdigest()
	ip = request.environ.get('REMOTE_ADDR')

	# Hand it to the database. It won't be valid until flag is changed.
	db.register(user, password, ip)
	return True

# Functions from here down require authentication.
def authenticate(username, password):
	user = request.POST['user']
	try:
		user = db.authorized_users[username]
		if user.pw_hash == sha512(password).hexdigest():
			return True
	except KeyError:
		pass
	return False

@route('/')
@auth_basic(authenticate)
def index():
	return 'Yep, this is the server.'

@route('/hash/<video_hash>')
@auth_basic(authenticate)
def check_for_video(video_hash):
	if db.video_exists(video_hash):
		return True
	return False

@route('/upload', method='POST')
@auth_basic(authenticate)
def upload():
	video = request.POST['video']
	video_start = request.POST['date']
	video_length = length(video)
	video_hash = sha512(video).hexdigest()
	try:
		db.insert_video_data(video_hash, video_start, video_length)
	except: #FIXME This should be just be a primary key collision error.
		return False
	return True

if __name__ == '__main__':
	run(host='127.0.0.1', port=8101)
