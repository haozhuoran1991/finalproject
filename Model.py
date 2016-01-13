__author__ = 'Jerry'
from google.appengine.ext import ndb

class User(ndb.Model):
    uName = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    pwd = ndb.StringProperty(required=True)
    friend= ndb.StringProperty(repeated=True)
    flag=ndb.BooleanProperty(default=False)

class Message(ndb.Model):
    sender = ndb.StringProperty()
    receiver = ndb.StringProperty()
    message = ndb.TextProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    @classmethod
    def query_message(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.timestamp)

    def str(self):
        return "%s : %s" %(self.sender, self.message)

class Session(ndb.Model):
  userKey = ndb.KeyProperty()