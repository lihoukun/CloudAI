from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.pool import SingletonThreadPool
import os
import datetime

if os.environ.get('FLASK_DB'):
    engine = create_engine('sqlite:////{}'.format(os.environ.get('FLASK_DB')),
                           convert_unicode=True, poolclass=SingletonThreadPool)
else:
    engine = create_engine('sqlite:////{}/sqlite3.db'.format(os.path.dirname(os.path.abspath(__file__))),
                           convert_unicode=True, poolclass=SingletonThreadPool)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class TrainingModel(Base):
    __tablename__ = 'trainings'
    id = Column(Integer, primary_key=True)
    name = Column(String(99), unique=True)
    num_gpu = Column(Integer)
    num_cpu = Column(Integer)
    bash_script = Column(String(9999))
    image_dir = Column(String(99))
    log_dir = Column(String(99))
    record_dir = Column(String(99))
    mnt_option = Column(String(99))
    params = Column(String(999))
    email = Column(String(99))
    status = Column(String(99))
    submit_at = Column(DateTime)
    start_at = Column(DateTime)
    stop_at = Column(DateTime)

    def __init__(self, name=None, num_gpu=0, num_cpu=0, bash_script=None, image_dir=None, log_dir=None,
                 record_dir=None, mnt_option=None, params=None, email=None, status=None):
        self.name = name
        self.num_gpu = num_gpu
        self.num_cpu = num_cpu
        self.bash_script = bash_script
        self.image_dir = image_dir
        self.log_dir = log_dir
        self.record_dir = record_dir
        self.mnt_option = mnt_option
        self.email = email
        self.status = status
        self.params = params
        self.submit_at = datetime.datetime.now()

    def __repr__(self):
        return '<Training %r>'.format(self.name)


class TemplateModel(Base):
    __tablename__ = 'templates'
    id = Column(Integer, primary_key=True)
    name = Column(String(99), unique=True)
    bash_script = Column(String(9999))
    image_dir = Column(String(99))
    log_dir = Column(String(99))
    mnt_option = Column(String(99))
    description = Column(String(999))

    def __init__(self, name=None, bash_script=None, image_dir=None, log_dir=None, mnt_option=None, description=None):
        self.name = name
        self.bash_script = bash_script
        self.image_dir = image_dir
        self.log_dir = log_dir
        self.mnt_option = mnt_option
        self.description = description

    def __repr__(self):
        return '<Template {}>'.format(self.name)


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()


