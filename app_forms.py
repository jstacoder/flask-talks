from wtforms import Form, fields, validators

class AddTalkForm(Form):
    title = fields.StringField(
            'Talk Title',
            validators = [
                validators.InputRequired()
            ]
    )

    topics = fields.HiddenField('topics')
    sub_topics = fields.HiddenField('sub-topics')
    content_items = fields.HiddenField('content-items')


class AddTopicForm(Form):
    name = fields.StringField(
            'Topic Name',
            validators = [
                validators.InputRequired()
            ]
    )
    talk = fields.HiddenField('talk')

class AddContentForm(Form):
    order = fields.IntegerField('order',validators=[validators.InputRequired()])
    content = fields.TextAreaField('content')
    typecode = fields.SelectField('Type Code',choices=(('html','html'),('code','code'),('text','text'),('markdown','markdown')),validators=[validators.InputRequired()])
    bullet = fields.StringField('Bullet')
    sub = fields.HiddenField('sub')

class AddSubTopicForm(Form):
    name = fields.StringField(
            'SubTopic Name',
            validators = [
                validators.InputRequired()
            ]
    )
    topic = fields.HiddenField('topic')
