from sqlalchemy import Column, Integer, String
from database import Base

class TrainingModel(Base):
    __tablename__ = 'trainings'
    id = Column(Integer, primary_key=True)
    name = Column(String(99), unique=True)
    num_gpu = Column(Integer)
    num_cpu = Column(Integer)
    num_epoch = Column(Integer)
    bash_script = Column(String(9999))
    image_dir = Column(String(99))
    log_dir = Column(String(99))
    mnt_option = Column(String(99))
    email = Column(String(99))
    status = Column(String(99))

    def __init__(self, name=None, num_gpu=0, num_cpu=0, num_epoch=None, bash_script=None, image_dir=None, log_dir=None,
                 mnt_option=None, email=None, status=None):
        self.name = name
        self.num_gpu = num_gpu
        self.num_cpu = num_cpu
        self.num_epoch = num_epoch
        self.bash_script = bash_script
        self.image_dir = image_dir
        self.log_dir = log_dir
        self.mnt_option = mnt_option
        self.email = email
        self.status = status

    def __repr__(self):
        return '<Training %r>' % (self.name)

    #@validates('num_gpu')
    #def validate_num_gpu(self, key, value):
    #    assert int(value) > 0


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
        return '<Template %r>' % (self.name)

