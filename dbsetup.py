# coding: utf-8
import os
from dbconn import get_connection,get_connection_and_dbname,get_default_db
from mongoengine import (
        Document, EmbeddedDocument, EmbeddedDocumentField , 
        EmbeddedDocumentListField, StringField , IntField, 
        BooleanField, EmailField , DateTimeField, DictField, 
        ListField, ReferenceField, pre_init, post_init,DynamicField,
        ReferenceField
)
from content_types import (
            TextContent,HTMLContent,CodeContent,
            ImageContent,VideoContent,URLContent,
            PDFContent
)

class ContentItem(Document):
    content = DynamicField()
    '''
        type_code can be one of: text, html, code, or media
    '''
    type_code = StringField(max_length=255,default="text")

class SubTopic(Document):
    name = StringField(max_length=255,unique=True)
    content_items = ListField(ReferenceField(ContentItem))

class SubTopicOrderItem(EmbeddedDocument):
    content_item = ReferenceField(ContentItem)
    order = IntField(required=True)
           
class SubTopicOrder(Document):
    order_items = EmbeddedDocumentListField(SubTopicOrderItem)
    sub_topic = ReferenceField(SubTopic)

    def get_items(self,reverse=False):
        items = []
        for idx in range(len(self.order_items)):
            for itm in self.order_items:
                if itm.order == (idx+1):
                    if not itm in items:
                        items.append(itm)
        return items if not reverse else reversed(items)

    def save(self,sub_topic,order_map,*args,**kwargs):
        self.sub_topic = sub_topic
        for itm in sub_topic.content_items:
            order_item = SubTopicOrderItem()
            order_item.content_item = itm
            order_item.order = order_map[str(itm.id)]
            self.order_items.append(order_item)
        return super(SubTopicOrder,self).save(*args,**kwargs)

class Topic(Document):
    name = StringField(max_length=255,unique=True)
    sub_topics = ListField(ReferenceField(SubTopic))
    
class Talk(Document):
    name = StringField(max_length=255,unique=True)
    topics = ListField(ReferenceField(Topic))


#pre_init.connect(_pre)

def main():
    #from t3 import MONGOLAB_URI
    #conn = connect(MONGOLAB_URI)
    #data = _get_conn_from_uri(MONGOLAB_URI)
    #conn = connect(data)
    #conn = connect(MONGOLAB_URI)
    #dbname,conn = get_connection_and_dbname()
    #db = conn[dbname]
    #conn.drop_database(db)
    db = get_default_db()
    if len(Talk.objects.all()) == 0:
        #_pre(document=ContentType)
        itm1 = ContentItem()
        itm1.content = 'xxxxx'
        itm1.save()
        itm2 = ContentItem()
        itm2.content = 'yyyyy'
        itm2.save()
        order = {
            str(itm2.id):0,
            str(itm1.id):1,
        }
        o = SubTopicOrder()
        sub = SubTopic(name='programming',content_items=[itm1,itm2]).save()
        o.save(sub,order)
        topic = Topic(name='Python',sub_topics=[sub]).save()
        talk = Talk(name='first_talk',topics=[topic]).save()        
    print Talk.objects.all()


if __name__ == "__main__":
    main()
