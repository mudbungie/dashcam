# Database backend for dashcam synchronization.
# Tables:
# 	users: username, password, registration_ip, authorized
#		videos:	file_hash, path, upload_time, upload_name, size

import sqlalchemy as sqla
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

engine = create_engine('sqlite:///dashcam.db')
meta = MetaData()
Base = declarative_base(metadata=meta)
Session = sqla.orm.sessionmaker(bind=engine)

class User(Base):
	__tablename__ = 'users'
	username = Column(String(32), primary_key=True) # Is a UUID.
	password = Column(String(129)) # Is a sha512 hex digest.
	registration_ip = Column(String(39)) # Because IPv6-compatible, why not?
	registration_date = Column(DateTime)
	authorized = Column(Boolean, default=False)

class Video(Base):
	__tablename__ = 'videos'
	video_hash = Column(String(129), primary_key=True) # sha512
	path = Column(Text)
	upload_time = Column(DateTime)
	upload_name = Column(Text)
	size = Column(Integer)

if __name__ == '__main__':
	Base.metadata.create_all(engine)
	

# Front-end for importation and reference.
class db:
	def __init__(self):
		Base.metadata.create_all(engine)
		self.s = Session

	def register(self, username, password, ip):
		s = self.s()
		try:
			user = User(username=username, password=password, registration_ip=ip,
				registration_date=datetime.now())
			s.add(user)
			s.commit()
			s.close()
		except:
			#FIXME Catch collision errors
			raise
	
	@property
	def users(self):
		s = self.s()
		us = [u.__dict__ for u in s.query(User).all()]
		s.close()
		return us

	@property
	def authorized_users(self):
		return [u for u in self.users if u['authorized']]

	def video_exists(self, video_hash):
		s = self.s()
		if s.query(Video).filter(video_hash=video_hash).one_or_none():
			exists = True
		else:
			exists = False
		s.close()
		return exists
		
	def insert_video_data(self, video_hash, upload_name, video_size):
		s = self.s()
		video = Video(video_hash=video_hash, path='videos/'+video_hash, 
			upload_time=datetime.now(), upload_name=upload_name, size=video_size)
		s.add(video)
		s.commit()



