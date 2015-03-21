from app import db
from app.models import *

with open ("drop_tables.sql", "r") as myfile:
	schema = myfile.read().replace('\n', '')
	result = db.engine.execute(schema)

db.engine.execute(schema)

# create the database and the db table
db.create_all()

user1 = users("123", "tona.arbeiter@gmail.com", "Arbeiter", "Tona")
user2 = users("123", "vannesa.glassford@hotmail.com", "Glassford", "Vannesa")
user3 = users("123", "aracelis@gmail.com", "James", "Aracelis")
main_user = users("123", "main@test.com", "User", "Main")
db.session.add(user1)
db.session.add(user2)
db.session.add(user3)
db.session.add(main_user)
db.session.commit()




