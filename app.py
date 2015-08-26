import os
from dbsetup import Topic,SubTopic,Talk,ContentItem
from flask import views
import flask


app = flask.Flask(__name__)


class AddTalkView(views.MethodView):
    def post(self):
        pass 


if __name__ == "__main__":
    port = int(os.environ.get('PORT',5555))
    app.run(host='0.0.0.0',port=port,debug=True)
        

