# coding: utf-8
import os
from mongoengine import (
        Document, EmbeddedDocument, EmbeddedDocumentField , 
        EmbeddedDocumentListField, StringField , IntField, 
        BooleanField, EmailField , DateTimeField, DictField, 
        ListField, ReferenceField, connect, pre_init, post_init
)

MONGODB_NAME = 'testdb'

if os.environ.get('MONGOLAB_URI'):
    connect(os.environ.get('MONGOLAB_URI'))
else:
    conn = connect(db=MONGODB_NAME)
    if MONGODB_NAME in conn.database_names():
        conn.drop_database(MONGODB_NAME)
    conn.close()
    conn = connect(db=MONGODB_NAME)


def _post(*args,**kwargs):
    print args
    print 'TEARING DOWN SETUP!@@@!!'
    print kwargs



class ContentType(Document):
    name = StringField(max_length=255,unique=True)
    content_class = StringField(max_length=255,required=True)

class ContentItem(EmbeddedDocument):
    name = StringField(max_length=255,unique=True)
    content_type = ReferenceField(ContentType)
    content_reference = StringField(max_length=255,unique=True,required=True)

class SubTopic(EmbeddedDocument):
    name = StringField(max_length=255,unique=True)
    content_items = EmbeddedDocumentListField(ContentItem)

class Topic(EmbeddedDocument):
    name = StringField(max_length=255,unique=True)
    sub_topics = EmbeddedDocumentListField(SubTopic)
    
class Talk(Document):
    name = StringField(max_length=255,unique=True)
    topics = EmbeddedDocumentListField(Topic)



#types: text,html,code,image,video,url,pdf

first = True

def _pre(*args,**kwargs):
    global first
    print 'SETTING UP DATABASE {}'.format(kwargs.get('document')._class_name)
    #if kwargs['document'] is ContentType:
    if first:
        first = False
        types = []
        _types = [
            'text','html','code','image','video','url','pdf'   
        ]
        _classes = [
            'TextContent','HTMLContent','CodeContent','ImageContent','VideoContent','URLContent','PDFContent'
        ]
        for t in _types:
            ContentType(**dict(name=t,content_class=_classes[_types.index(t)])).save()
        print 'Done adding default content-types'


post_init.connect(_post)
pre_init.connect(_pre)


itm = ContentItem(name='justtst',content_type=ContentType.objects(name='text').first(),content_reference='refkey')
sub = SubTopic(name='programming',content_items=[itm])
topic = Topic(name='Python',sub_topics=[sub])
talk = Talk(name='first_talk',topics=[topic])
talk.save()
talks = Talk.objects.all()
