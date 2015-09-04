import os
from inflection import pluralize
from dbsetup import Topic,SubTopic,Talk,ContentItem,EditMode
from dbconn import get_connection_and_dbname, get_default_db
from app_forms import AddTalkForm,AddTopicForm,AddContentForm,AddSubTopicForm
from flask import views,g
import json
import flask
import bson
from csrf import crossdomain
from markdown2 import markdown as md
import jinja2_highlight
from click_counter import get_counter,cache_count,check_cache,set_session,check_session

get_edit_mode = lambda: hasattr(g,'edit_mode') and getattr(g,'edit_mode') or True

change_mode = lambda: setattr(g,'edit_mode',(not getattr(g,'edit_mode')))

edit_on = lambda: setattr(EditMode.get(),'is_active',True) and EditMode.get().save()
edit_off = lambda: setattr(EditMode.get(),'is_active',False) and EditMode.get().save()
is_edit = lambda: EditMode.get().is_active

add_click = get_counter('flask-talks.herokuapp.com')

def get_by_id(model,_id):
    obj = model.objects(id=_id)
    return (len(obj)>0) and obj[0]

class MyFlask(flask.Flask):
    jinja_opts = dict(flask.Flask.jinja_options)
    jinja_opts.setdefault('extensions',
            []).append('jinja2_highlight.HighlightExtension')

def add_talk(name,topics=None):
    talk = Talk(name=name)
    if topics is not None:
        for t in topics:
            if not type(t) == Topic:
                _topic = t['topic']
                _subs = t['sub_topics']
                add_topic(talk,_topic,_subs)
            else:
                add_topic(talk,t)
    return talk.save()

def add_topic(talk,name,sub_topics=None):
    topic = Topic(name=name).save() if type(name) == str else name
    if sub_topics is not None:
        for s in sub_topics:
            add_sub_topic(topic,s['name'],s['content_items'])
    talk.topics.append(topic)
    return talk

def add_sub_topic(topic,name,content_items=None):
    sub_topic = SubTopic(name=name)
    if content_items is not None:
        for c in content_items:
            add_content_to_subtopic(sub_topic,c['content'],c['order'])
    topic.sub_topics.append(sub_topic)
    return topic.save()

def add_content_item(content,order):
    return ContentItem(content=content,order=order).save()
    
def add_content_to_subtopic(sub_topic,content,order=None):
    if not type(content) == ContentItem:
        order = sub_topic.content_items.count() if order is None else order
        content = add_content_item(content,order)
    sub_topic.content_items.append(content)
    return sub_topic.save()


app = MyFlask(__name__)
api = flask.Blueprint('api','api',url_prefix='/api/v1')


@app.template_filter()
def markdown(s):
    return md(s)

@app.template_filter()
def plural(s):
    return pluralize(s)

@app.before_request
def connect_redis():
    if not check_cache():
        cache_count()
        add_click()
        print 'added click'

class AddTalkView(views.MethodView):
    decorators = [crossdomain(origin='*')]
    def post(self):
        add_talk(request.form.get('title'),request.form.get('topics'))

    def get(self):
        talks = [dict(json.loads(x.to_json())) for x in Talk.objects.all()]
        return flask.jsonify(talks=talks)

class AddTalksView(views.MethodView):
    decorators = [crossdomain(origin='*')]
    _model = Talk

    def post(self):
        print str(flask.request.form)
        print str(flask.request.json)
        talk = self._model(name=flask.request.json['name']).save()
        return flask.jsonify(talk=json.loads(talk.to_json()))

class AddTopicView(views.MethodView):
    def post(self):
        talk = Talk.objects(id=flask.request.form['talk_id'])
        talk = (len(talk)>0) and talk[0]
        topic = Topic(name=flask.request.form['name']).save()
        talk.topics.append(topic)
        talk.save()
        return flask.jsonify(talk=json.loads(talk.to_json()))

class AddSubTopicView(views.MethodView):
    def post(self):
        topic = Topic.objects(id=flask.request.form['topic_id'])
        topic = (len(topic)>0) and topic[0]
        sub_topic = SubTopic(name=flask.request.form['name']).save()
        topic.sub_topics.append(sub_topic)
        topic.save()
        return flask.jsonify(topic=json.loads(topic.to_json()))

class AddContentView(views.MethodView):
    def post(self):
        sub_topic = SubTopic.objects(id=flask.request.form['sub_topic_id'])
        sub_topic = (len(sub_topic)>0) and sub_topic[0]
        content = ContentItem(content=flask.request.form['content'],order=flask.request.form['order'],bullet=flask.request.form['bullet']).save()
        sub_topic.content_items.append(content)
        sub_topic.save()
        return flask.jsonify(sub_topic=json.loads(sub_topic.to_json()))

class TstView(views.MethodView):
    def post(self):
        c = ContentItem(**flask.request.form).save()
        return flask.jsonify(talk=c.to_json())

class ShowView(views.MethodView):
    _model = None

    def get(self,item_id=None):
        item_name = self._model.__name__.lower()
        if item_id is None:
            item_name = pluralize(item_name)
        item = dict(json.loads(self._model.objects(id=item_id)[0].to_json())) if item_id is not None else [dict(json.loads(x.to_json())) for x in self._model.objects.all()]
        return flask.jsonify({item_name:item})

class ShowTalkView(ShowView):

    decorators = [crossdomain(origin='*')]

    _model = Talk

class ShowContentItemView(ShowView):
    _model = ContentItem

class ShowTopicView(ShowView):
    _model = Topic

class ShowSubTopicView(ShowView):
    _model = SubTopic

class ChangeEditMode(views.MethodView):

    def get(self,talk_id):
        dict(
            on=edit_on,
            off=edit_off
        )[flask.request.args['edit_mode']]()
        return flask.redirect(flask.url_for('front.view_talk',talk_id=talk_id))

api.add_url_rule('/talks/','index',view_func=AddTalkView.as_view('index'))
api.add_url_rule('/talks/<item_id>','show_talk',view_func=ShowTalkView.as_view('show_talk'))
api.add_url_rule('/topics/','topics',view_func=ShowTopicView.as_view('topics'))
api.add_url_rule('/topics/<item_id>','show_topics',view_func=ShowTopicView.as_view('show_topics'))
api.add_url_rule('/subtopics/','subtopics',view_func=ShowSubTopicView.as_view('subtopics'))
api.add_url_rule('/subtopics/<item_id>','show_subtopics',view_func=ShowSubTopicView.as_view('show_subtopics'))
api.add_url_rule('/content/','content',view_func=ShowContentItemView.as_view('content'))
api.add_url_rule('/content/<item_id>','show_content_item',view_func=ShowContentItemView.as_view('show_content_item'))
api.add_url_rule('/test/','show_test',view_func=TstView.as_view('test'))
api.add_url_rule('/test_talk','talk_test',view_func=AddContentView.as_view('talk_test'))
api.add_url_rule('/talks/add/','add_talk',view_func=AddTalksView.as_view('add_talk'))
api.add_url_rule('/topics/add/','add_topic',view_func=AddTopicView.as_view('add_topic'))
api.add_url_rule('/subtopics/add/','add_sub',view_func=AddSubTopicView.as_view('add_sub'))
api.add_url_rule('/content/add/','add_content',view_func=AddContentView.as_view('add_content'))
api.add_url_rule('/edit_mode/<talk_id>/','edit_mode',view_func=ChangeEditMode.as_view('edit_mode'))



app.register_blueprint(api)

@app.context_processor
def add_get_id():
    return {
            'get_id':lambda itm: hasattr(itm,'_id') and getattr(getattr(itm,'_id'),'$id')
           }

front = flask.Blueprint('front','front',url_prefix='/talks',template_folder='templates')

@front.before_app_request
def add_edit_mode():
    g.edit_mode = get_edit_mode()
    app.jinja_env.globals['is_edit_mode'] = is_edit()

class FrontIndexView(views.MethodView):

    def get(self):
        talk_names = [{'name':t.name,'id':str(t.id)} for t in  Talk.objects.all()]    
        return flask.render_template('front.html',talk_names=talk_names)

class FrontTalkView(views.MethodView):

    def get(self,talk_id):
        talk = Talk.objects(id=talk_id)
        talk = (len(talk)>0) and talk[0]
        rtn = format_talk(talk.to_json())
        return flask.render_template('talks.html',talk=rtn,talk_id=talk_id,is_edit_mode=is_edit())

class FrontAddTalkView(views.MethodView):

    def get(self):
        form = AddTalkForm()
        return flask.render_template('add-talk.html',form=form)

class FrontAddTopicView(views.MethodView):

    def get(self,talk_id):
        form = AddTopicForm(talk=talk_id)
        return flask.render_template('add-topic.html',form=form)

    def post(self,talk_id):
        talk = get_by_id(Talk,talk_id)
        form = flask.request.form
        topic = Topic(name=form['name']).save()
        talk.topics.append(topic)
        talk.save()
        return flask.redirect(flask.url_for('.view_talk',talk_id=talk_id))

class FrontAddSubTopicView(views.MethodView):

    def get(self,topic_id):
        form = AddSubTopicForm(topic=topic_id)
        return flask.render_template('add-sub-topic.html',form=form)

    def post(self,topic_id):
        topic = get_by_id(Topic,topic_id)
        form = flask.request.form
        sub_topic = SubTopic(name=form['name']).save()
        topic.sub_topics.append(sub_topic)
        topic.save()
        return flask.redirect(flask.url_for('.view_topic',topic_id=topic_id))

class FrontAddContentView(views.MethodView):

    def get(self,sub_id):
        form = AddContentForm(sub=sub_id,order=0)
        return flask.render_template('add_content.html',form=form)

    def post(self,sub_id):
        sub = get_by_id(SubTopic,sub_id)
        form = flask.request.json    
        r = flask.request
        content = ContentItem(content=form['content'],bullet=form['bullet'],type_code=form['type_code'],order=form['order']).save()
        sub.content_items.append(content)
        sub.save()
        return flask.redirect(flask.url_for('.view_sub',sub_id=sub_id))

class FrontContentView(views.MethodView):
    def get(self,content_id):
        content = get_by_id(ContentItem,content_id)
        sub = filter(lambda x: content in x.content_items,SubTopic.objects.all())[0]
        topic = filter(lambda x: sub in x.sub_topics,Topic.objects.all())[0]
        talk = filter(lambda x: topic in x.topics,Talk.objects.all())[0]
        other_items = []
        for sub in topic.sub_topics:
            if type(sub) == SubTopic:
                [other_items.append(x) for x in sub.content_items]
        idx = other_items.index(content)
        prev_item = (len(other_items) > 1 and idx != 0) and other_items[idx-1].id
        next_item = (len(other_items) >= 2 and idx != (len(other_items)-1)) and other_items[idx+1].id
        is_code = content.type_code == 'code'
        is_html = content.type_code == 'html'
        is_image = content.type_code == 'image'
        is_markdown = content.type_code == 'markdown'
        return flask.render_template(
                                'content.html',
                                content = content.content.strip(),
                                is_code = is_code,
                                prev_id = prev_item,
                                next_id = next_item,
                                talk = talk,
                                is_html = is_html,
                                is_markdown = is_markdown,
                                is_image = is_image,
        )

class FrontTopicView(views.MethodView):
    def get(self,topic_id):
        topic = get_by_id(Topic,topic_id)
        talk = filter(lambda x: topic in x.topics,Talk.objects.all())[0]
        return flask.render_template('topic.html',topic=topic,talk=talk)

class FrontSubView(views.MethodView):
    def get(self,sub_id):        
        sub = get_by_id(SubTopic,sub_id)
        topic = filter(lambda x: sub in x.sub_topics,Topic.objects.all())[0]
        sub = dict(content_items=filter(lambda x: type(x) != bson.dbref.DBRef,sub.content_items),name=sub.name,id=sub_id)
        return flask.render_template('sub.html',sub=sub,topic=topic)


class EditView(views.MethodView):
    _model = None
    _form = None
    _edit_template = None
    _endpoint = None
    _query_arg = {}

    def get(self,obj_id):
        obj = get_by_id(self._model,obj_id)
        form = self._form(obj=obj)
        return flask.render_template(self._edit_template,form=form,obj=obj,is_edit=True)


    def post(self,obj_id):
        obj = get_by_id(self._model,obj_id)
        for attr in dir(obj):
            if not attr.startswith('_'):
                if attr in flask.request.form:
                    val = flask.request.form[attr]
                    if val:
                        setattr(obj,attr,val)
        obj.save()
        if self._query_arg:
            if type(self._query_arg) == str:
                self._query_arg = { 
                        self._query_arg:flask.request.args[self._query_arg]
                }
            else:
                self._query_arg = {
                    x:flask.request.args[x] for x in self._query_arg
                }
        return flask.redirect(flask.url_for(self._endpoint,**self._query_arg))        

class EditContentView(EditView):
    _model = ContentItem
    _form = AddContentForm
    _endpoint = '.view_sub'
    _edit_template = 'add_content.html'
    _query_arg = 'sub_id'


class DeleteView(views.MethodView):
    '''
        generic delete view

        _model => Model to delete
        _endpoint => endpoint to redirect after deleting 
        _query_arg => args needed when redirecting
    '''
    _model = None
    _endpoint = '.index'
    _query_arg = {}

    def get(self,obj_id):
        obj = get_by_id(self._model,obj_id)
        obj.delete()
        if self._query_arg:
            if type(self._query_arg) == str:
                self._query_arg = { 
                        self._query_arg:flask.request.args[self._query_arg]
                }
            else:
                self._query_arg = {
                    x:flask.request.args[x] for x in self._query_arg
                }
        return flask.redirect(flask.url_for(self._endpoint,**self._query_arg))        

class DeleteTalkView(DeleteView):
    _model = Talk

class DeleteTopicView(DeleteView):
    _model = Topic
    _endpoint = '.view_talk'
    _query_arg = 'talk_id'

class DeleteContentView(DeleteView):
    _model = ContentItem
    _endpoint = '.view_sub'
    _query_arg = 'sub_id'


front.add_url_rule('/','index',view_func=FrontIndexView.as_view('index'))
front.add_url_rule('/view/<talk_id>/','view_talk',view_func=FrontTalkView.as_view('view_talk'))
front.add_url_rule('/add/','add_talk',view_func=FrontAddTalkView.as_view('add_talk'))
front.add_url_rule('/view/content/<content_id>/','view_content',view_func=FrontContentView.as_view('view_content'))
front.add_url_rule('/view/topic/<topic_id>/','view_topic',view_func=FrontTopicView.as_view('view_topic'))
front.add_url_rule('/view/sub/<sub_id>/','view_sub',view_func=FrontSubView.as_view('view_sub'))
front.add_url_rule('/content/add/<sub_id>/','add_content',view_func=FrontAddContentView.as_view('add_content'))
front.add_url_rule('/topic/add/<talk_id>/','add_topic',view_func=FrontAddTopicView.as_view('add_topic'))
front.add_url_rule('/subtopic/add/<topic_id>/','add_subtopic',view_func=FrontAddSubTopicView.as_view('add_subtopic'))
front.add_url_rule('/delete/<obj_id>/','delete_talk',view_func=DeleteTalkView.as_view('delete_talk'))
front.add_url_rule('/delete/topic/<obj_id>/','delete_topic',view_func=DeleteTopicView.as_view('delete_topic'))
front.add_url_rule('/delete/content/<obj_id>/','delete_content',view_func=DeleteContentView.as_view('delete_content'))
front.add_url_rule('/edit/content/<obj_id>/','edit_content',view_func=EditContentView.as_view('edit_content'))



app.register_blueprint(front)

def format_talk(talk_data):
    if type(talk_data) == str:
        talk_data = json.loads(talk_data)
    title = talk_data['name']
    talk_id = talk_data['_id']['$oid']
    topics = talk_data['topics']
    sub_topics = {x['_id']["$oid"]:x['sub_topics'] for x in topics}
    content_items = {}
    for t in topics:
        for s in sub_topics[t['_id']['$oid']]:
            if content_items.get(s['_id']['$oid']):
                content_items[s['_id']['$oid']].extend(s['content_items'])
            else:
                content_items[s['_id']['$oid']] = s['content_items']    
    return dict(title=title,topics=topics,sub_topics=sub_topics,content_items=content_items,talk_id=talk_id)

def display_talk(formatted_talk):
    print formatted_talk['title']+'\n\n'
    for t in formatted_talk['topics']:
        print '\t'+t['name']+'\n\n'
        for s in formatted_talk['sub_topics'][t['_id']['$oid']]:
            print '\t\t'+s['name']+'\n\n'
            for content in formatted_talk['content_items'][s['_id']['$oid']]:
                print '\t\t\t'+content['content']

def get_display_talk(formatted_talk):
    rtn = ''
    rtn += "\nTalk Title: "+formatted_talk['title']+'\n\nTopics:\n'
    for t in formatted_talk['topics']:
        rtn += '\t'+t['name']+'\n\n'
        for s in formatted_talk['sub_topics'][t['_id']['$oid']]:
            rtn += '\n\t\t'+s['name']
            for content in formatted_talk['content_items'][s['_id']['$oid']]:
                rtn += '\n\t\t\t'+content['content']
    return rtn

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://ang.com'
    return response


if __name__ == "__main__":


    print os.path.dirname(__file__)
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
