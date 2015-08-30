# coding: utf-8
import os
import json
from dbconn import get_connection,get_connection_and_dbname,get_default_db
from mongoengine import (
        Document, EmbeddedDocument, EmbeddedDocumentField , 
        EmbeddedDocumentListField, StringField , IntField, 
        BooleanField, EmailField , DateTimeField, DictField, 
        ListField, ReferenceField, pre_init, post_init,DynamicField,
        ReferenceField
)

class ContentItem(Document):
    content = DynamicField()
    '''
        type_code can be one of: text, html, code, or media
    '''
    type_code = StringField(max_length=255,default="text")
    bullet = StringField(max_length=50,default='A note about the topic')
    order = IntField(required=True)

class SubTopic(Document):
    name = StringField(max_length=255,unique=True)
    content_items = ListField(ReferenceField(ContentItem))

    def to_json(self):
        rtn = super(SubTopic,self).to_json()
        rtn = json.loads(rtn)
        rtn['content_items'] = [json.loads(x.to_json()) for x in self.content_items]
        return json.dumps(rtn)

    def get_content(self,reverse=False):
        rtn = []
        for idx in range(len(self.content_items)):
            for c in self.content_items:
                if c.order == idx:
                    rtn.append(c)
        return rtn if not reverse else reversed(rtn)

class Topic(Document):
    name = StringField(max_length=255,unique=True)
    sub_topics = ListField(ReferenceField(SubTopic))

    def to_json(self):
        rtn = super(Topic,self).to_json()
        rtn = json.loads(rtn)
        rtn['sub_topics'] = [json.loads(x.to_json()) for x in self.sub_topics]
        return json.dumps(rtn)

class Talk(Document):
    name = StringField(max_length=255,unique=True)
    topics = ListField(ReferenceField(Topic))

    def to_json(self):
        rtn = super(Talk,self).to_json()
        rtn = json.loads(rtn)
        rtn['topics'] = [json.loads(x.to_json()) for x in self.topics if type(x) == Topic]
        return json.dumps(rtn)

def main():
    db = get_default_db()
    if len(Talk.objects.all()) == 0:
        itm1 = ContentItem()
        itm1.content = 'def a_py_func():\n\tprint "hello world"'
        itm1.order = 1
        itm1.save()
        itm2 = ContentItem()
        itm2.content = 'def a_py_func():\n\tprint "hello world"'
        itm2.order = 0
        itm2.save()
        sub = SubTopic(name='programming',content_items=[itm1,itm2]).save()
        topic = Topic(name='Python',sub_topics=[sub]).save()
        talk = Talk(name='first_talk',topics=[topic]).save()        
    t = Talk.objects.all()[0]
    print '{}:\n\n\t'.format(t.topics[0].sub_topics[0].name)+'\n\t'.join(map(str,map(lambda x: x.content,t.topics[0].sub_topics[0].get_content())))

if __name__ == "__main__":
    main()
