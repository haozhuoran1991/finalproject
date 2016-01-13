#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import urllib
import webapp2
import jinja2
from webapp2_extras import security
from Model import User, Message, Session
from google.appengine.ext import ndb


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader([os.path.dirname(__file__),os.path.dirname(__file__)+"/templates"]))
#init User
tom=User(id='tom@gmail.com',uName='Tom',email='tom@gmail.com',pwd='123',friend=['Jerry','Lucy','Emma'])
jerry=User(id='jerry@gmail.com',uName='Jerry',email='jerry@gmail.com',pwd='123',friend=['Tom','Lucy','Emma'])
lucy=User(id='lucy@gmail.com',uName='Lucy',email='lucy@gmail.com',pwd='123',friend=['Tom','Jerry','Emma'])
emma=User(id='emma@gmail.com',uName='Emma',email='emma@gmail.com',pwd='123',friend=['Tom','Lucy','Jerry'])
tom.put()
jerry.put()
lucy.put()
emma.put()
#init Message
m1=Message(sender="Jerry",receiver="Tom",message="hello tom!")
m2=Message(sender="Tom",receiver="Jerry",message="Hi Jerry! what's up?")
m3=Message(sender="Tom",receiver="Emma",message="Hi Emma! what's up?")
key_m1=m1.put()
# print('call put')
key_m2=m2.put()
# print('call put')
key_m3=m3.put()
# print('call put')
#handeler
class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())

class SignUpHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('signup.html')
        self.response.write(template.render())

    def post(self):
        username=self.request.get("uname")
        uemail=self.request.get("email")
        upwd=self.request.get("pwd")
        if username == '' or uemail=='' or upwd=='':
            self.redirect('/error')
        else:
            user=User.get_by_id(uemail)
            if user:
                self.redirect('/error')
            else:
                newUser=User(id=uemail,uName=username,email=uemail,pwd=upwd)
                token = security.generate_random_string(length=20)
                session = Session(id=token)
                session.userKey=newUser.put()
                session.put()
                self.response.set_cookie(key='token', value=token, path='/')
                self.redirect('/home')


class LoginHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render())

    def post(self):
        uemail=self.request.get('email')
        upwd=self.request.get('pwd')
        if uemail=='' or upwd=='':
            self.redirect('/error')

        else:
            user = ndb.Key('User',uemail).get()
            if user and user.pwd==upwd:
                token = security.generate_random_string(length=20)
                session = Session(id=token)
                session.userKey=user.put()
                session.put()
                self.response.set_cookie(key='token', value=token, path='/')
                self.redirect("/home")

            else:
                self.redirect("/login")

class HomeHandler(webapp2.RequestHandler):
    def get(self):
        token = self.request.cookies.get("token")
        email = ndb.Key('Session',token).get().userKey.id()
        user=User.get_by_id(email)
        friends=[]
        for friend in user.friend:
            fuser=User.query(User.uName==friend).get()
            friends.append(fuser)
        template_values = {
                'UserName': user.uName,
                'friends':friends,

        }
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(template_values))


    def post(self):
        pass





class ErrorHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('error.html')
        self.response.write(template.render())

class SearchHandler(webapp2.RequestHandler):

    def get(self):
        token = self.request.cookies.get("token")
        email = ndb.Key('Session',token).get().userKey.id()
        user=User.get_by_id(email)
        Email=self.request.get('search')
        searchfriend=User.get_by_id(Email)
        if searchfriend:
            result=searchfriend.uName
            related_people=searchfriend.friend
            flag=True
        else:
            result='Not find Match Users'
            flag=False
            related_people=''
        template_values = {
                'UserName': user.uName,
                'result':result,
                'Flag':flag,
                'friends':related_people,

        }
        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))

    def post(self):
        userName=self.request.get('user')
        friendName=self.request.get('friend')
        user=User.query(User.uName==userName).get()
        find_friend=User.query(User.uName==friendName).get()
        uList=user.friend
        fList=find_friend.friend
        if friendName in uList:
            pass
        else:
            uList.append(friendName)
        if userName in fList:
            pass
        else:
            fList.append(userName)
        user.friend=uList
        find_friend.friend=fList
        user.put()
        find_friend.put()
        response=userName+' and '+friendName+' are friend now'
        # response=uList
        self.response.write(response)

class GetchatHandler(webapp2.RequestHandler):

    def post(self):
        talker=self.request.get("talker")
        user=self.request.get('user')
        friend=User.query(User.uName==talker).get()
        friend.flag=False
        friend.put()
        message=Message.query(ndb.OR(ndb.AND(Message.receiver==talker,Message.sender==user),ndb.AND(Message.receiver==user,Message.sender==talker))).order(Message.timestamp).fetch(40)
        response=''
        for m in message:
            response+=m.str()+'\n'

        print(talker)
        print(user)
        print(message)
        self.response.write(response)

class SendchatHandler(webapp2.RequestHandler):

    def post(self):
        send = self.request.get("send")
        rec = self.request.get("rec")
        mess = self.request.get("mess")
        friend=User.query(User.uName==send).get()
        friend.flag=True
        friend.put()
        newMessage=Message(sender=send,receiver=rec,message=mess)
        newkey=newMessage.put()
        message=Message.query(ndb.OR(ndb.AND(Message.receiver==rec,Message.sender==send),ndb.AND(Message.receiver==send,Message.sender==rec))).order(Message.timestamp).fetch(40)
        response='Message Send Success!'
        # for m in message:
        #     response+=m.str()+'\n'
        self.response.write(response)

class OutHandler(webapp2.RequestHandler):
    def get(self):
      token = self.request.cookies.get("token")
      if token:
        self.response.delete_cookie(key="token",path="/")
        name = ndb.Key("Session",token).get().userKey.id()
        ndb.Key("Session",token).delete()
      else:
        name = "<no one>"
      template_values = {
                'n': name,
        }
      template = JINJA_ENVIRONMENT.get_template('logout.html')
      self.response.write(template.render(template_values))

class CheckHandler(webapp2.RequestHandler):
    def get(self):
        flags=''
        userName=self.request.get("user")
        user=User.query(User.uName==userName).get()
        Friends=user.friend
        for f in Friends:
            friend=User.query(User.uName==f).get()
            # friends=[]
            # friends.append(friend)
            flag=friend.flag
            flags+=flag+','
        response=flags
        self.response.write(response)
        # template_values = {
        #         'UserName': user.uName,
        #         'friends':friends,
        #
        # }
        # template = JINJA_ENVIRONMENT.get_template('home.html')
        # self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/signup', SignUpHandler),
    ('/login', LoginHandler),
    ('/home', HomeHandler),
    ('/error', ErrorHandler),
    ('/search', SearchHandler),
    ('/getchat', GetchatHandler),
    ('/sendchat', SendchatHandler),
    ('/out',OutHandler),
    ('/check',CheckHandler),



], debug=True)
