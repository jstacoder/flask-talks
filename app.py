import os
from dbsetup import Topic,SubTopic,Talk,ContentItem
from flask import views
import flask


def add_topic(talk,name,sub_topics=None):
    topic = Topic(name=name,sub_topics=sub_topics or [])
    talk.topics.append(topic)
    return talk.save()

def add_sub_topic(topic,name,content_items=None):
    sub_topic = SubTopic(name=name,content_items=content_items or [])
    topic.sub_topics.append(sub_topic)
    return topic

def add_content_item(sub_topic,name,content_type,content):
    item = ContentItem(name=name)
    item.set_content_type(content_type)
    item.set_content(content)
    sub_topic.content_items.append(item)
    return sub_topic

app = flask.Flask(__name__)


class AddTalkView(views.MethodView):
    def post(self):
        pass 


if __name__ == "__main__":
    port = int(os.environ.get('PORT',5555))
    app.run(host='0.0.0.0',port=port,debug=True)
        

