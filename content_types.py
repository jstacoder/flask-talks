

class Content(object):
    _content = None

    @property
    def content(self):
        raise NotImplemented

    def __init__(self,content):
        self._content = content
    
class TextContent(Content):
    @property
    def content(self):
        return str(self._content)

    
class HTMLContent(TextContent):
    pass

class CodeContent(Content):
    def __init__(self,content,language):
        self.language = language
        super(CodeContent,self).__init__(content)

class ImageContent(Content):
    pass

class VideoContent(Content):
    pass

class URLContent(Content):
    pass

class PDFContent(Content):
    pass
