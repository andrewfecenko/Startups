from app import db
from app.models import *

with open ("drop_tables.sql", "r") as myfile:
	schema = myfile.read().replace('\n', '')
	result = db.engine.execute(schema)

db.engine.execute(schema)

# create the database and the db table
db.create_all()

user1 = users("123", "test@test.com", "Fecenko", "Andrew")
db.session.add(user1)
db.session.commit()
idea1 = ideas("Startup Company 1", "Idea 1 Description", 3, 1, "tag1 tag2")
idea2 = ideas("Startup Company 2", "Idea 2 Description", 4, 1, "test test2")
db.session.add(idea1)
db.session.add(idea2)
db.session.commit()




