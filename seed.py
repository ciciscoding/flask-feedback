from models import db, User, Feedback
from app import app

db.drop_all()
db.create_all()

ct = User.register(username='cthomas', pwd='Thisisatest', email='ct@gmail.com', first='Cici', last='Thom')

bt = User.register(username='catslover13', pwd='Thisisatestpwd', email='boots@gmail.com', first='Boots', last='Thomas')

db.session.add_all([ct, bt])
db.session.commit()

f1 = Feedback(title='First Post', content='This is the first post, ready to give some feedback', author='cthomas')

f2 = Feedback(title='Here is another', content='Heres another feedback post to make sure it is going well', author='cthomas')

f3 = Feedback(title='First Post!', content='This is the first post, ready to give some feedback', author='catslover13')

f4 = Feedback(title='Ready to give some feedback', content='Heres another feedback post to make sure it is going well', author='catslover13')

db.session.add_all([f1, f2, f3, f4])
db.session.commit()