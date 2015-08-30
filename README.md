#Flask-Talks <br/>(Using Bootstrap V4.0alpha)

##A tool for use when giving presentations


Try out the demo on [heroku](https://flask-talks.herokuapp.com/talks/)

or just start the demo on your own heroku account with __One Click__!
[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

###App Structure

* `talks` are the main item that we will use in this app.

* Talks have a unique title and are made up of multiple `topics` 

* Topics have a unique name and are made up of multiple `sub_topics`

* Sub Topics have a unique name and are made up of multiple `content_items`

* Content Items are the lowest layer, they have a unique bullet, for links, an order, and a `content` field, for displayable content ie:
    - code
    - html
    - text
    - images

The idea behind the layered structure is the app will use this to create a summery for 
your talk. 
The summary is layed out like this:

##Talk Title

###First Topic name

  * ####First sub topic name
    1. [first content bullet](#)
    2. [Second content bullet](#)

  * ####Second sub topic name
    1. [first content bullet](#)
    2. [Second content bullet](#)

###Second Topic name

  * ####First sub topic name
    1. [first content bullet](#)
    2. [Second content bullet](#)

  * ####Second sub topic name
    1. [first content bullet](#)
    2. [Second content bullet](#)


each `content_item` bullet is a link to the content page for that `content_item`
If the `content_item.content` is code, it will be syntax highlighted, see the demp app for an example
