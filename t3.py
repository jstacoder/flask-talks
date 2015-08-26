from mongoengine import connect

MONGOLAB_URI = 'mongodb://heroku_vxrmrz45:fbknna6idqj6bvjc6v2a6ujfan@ds035593.mongolab.com:35593/heroku_vxrmrz45'

connect(host=MONGOLAB_URI)
