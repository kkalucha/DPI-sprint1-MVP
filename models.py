from app import db

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(), primary_key = True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return self.username

    def serialize(self):
        return {
            'username' : self.username,
            'pasword' : self.password
        }