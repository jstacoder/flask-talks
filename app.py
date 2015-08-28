import os
from dbsetup import Topic,SubTopic,Talk,ContentItem
from dbconn import get_connection_and_dbname, get_default_db
from flask import views,g
import json
import flask

def add_talk(name,topics=None):
    talk = Talk()
    talk.name = name
    if topics is not None:
        for t in topics:
            _topic = topics[t]['topic']
            _subs = topics[t]['sub_topics']
            add_topic(talk,_topic,_subs)
    return talk.save()

def add_topic(talk,name,sub_topics=None):
    topic = Topic(name=name)
    if sub_topics is not None:
        for s in sub_topics:
            add_sub_topic(topic,s['name'],s['content_items'])
    talk.topics.append(topic)
    return talk

def add_sub_topic(topic,name,content_items=None):
    sub_topic = SubTopic(name=name)
    if content_items is not None:
        for c in content_items:
            add_content_item(sub_topic,c['name'],c['content_type'],c['content'])        
    topic.sub_topics.append(sub_topic)
    return topic

def add_content_item(content):
    item = ContentItem(content=content)
    item.content = content
    return item.save()

def add_content_to_subtopic(sub_topic,content):
    if not type(content) == ContentItem:
        content = add_content_item(content)
    sub_topic.content_items.append(content)
    return sub_topic.save()


app = flask.Flask(__name__)
api = flask.Blueprint(__name__+'api','api',url_prefix='/api/v1')


#@app.before_first_request

def connect_redis(self):
    host = 'localhost'
    if 'REDISCLOUD_URL' in os.environ:
        host = os.environ.get('REDISCLOUD_URL')
    g._cache = Redis(host=host)

class AddTalkView(views.MethodView):
    def post(self):
        add_talk(request.form.get('title'),request.form.get('topics'))

    def get(self):
        talks = [dict(json.loads(x.to_json())) for x in Talk.objects.all()]
        return flask.jsonify(talks=talks)

class AddView(views.MethodView):
    _model = None

    def post(self):
        ins = get_from_form(self._model).save()

class TstView(views.MethodView):
    def post(self):
        c = ContentItem(**flask.request.form).save()
        return flask.jsonify(dict(json.loads(c.to_json())))

class ShowView(views.MethodView):
    _model = None

    def get(self,item_id=None):
        item = dict(json.loads(self._model.objects(id=item_id)[0].to_json())) if item_id is not None else [dict(json.loads(x.to_json())) for x in self._model.objects.all()]
        return flask.jsonify(item=item)

class ShowTalkView(ShowView):
    _model = Talk

class ShowContentItemView(ShowView):
    _model = ContentItem

api.add_url_rule('/talks/','index',view_func=AddTalkView.as_view('index'))
api.add_url_rule('/talks/<item_id>','show_talks',view_func=ShowTalkView.as_view('show_talks'))
api.add_url_rule('/content/','content',view_func=ShowContentItemView.as_view('content'))
api.add_url_rule('/content/<item_id>','show_content_item',view_func=ShowContentItemView.as_view('show_content_item'))
api.add_url_rule('/test/','show_test',view_func=TstView.as_view('test'))

app.register_blueprint(api)


if __name__ == "__main__":
    dbname, conn= get_connection_and_dbname()
    db = conn['test']
    topics = {
        'a': {
            'topic':'something',
            'sub_topics': [
                {
                    'name':'test',
                    'content_items':[
                        {
                            'name':'test1',
                            'content':'ttttt',
                        },
                        {
                            'name':'xxxxx',
                            'content':'dddd',
                        }
                    ]
                }
            ]
        }
    }
    #add_talk('testing_talk',topics)
    #db.talk.insert(topics)
    #print list(db.talk.find({}))
    port = int(os.environ.get('PORT',5555))
    app.run(host='0.0.0.0',port=port,debug=True)
        

