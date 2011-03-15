PubHubSubBub Developer Tutorial
===============================

welcome, this document contains an example application written in python
that will help you play with a pshb (pubsubhubbub from now on) hub and
an application that publishes its content to it.

Requirements
------------

 * python >= 2.5 (I'm using 2.6.1)
 * git (for the example)
 * subversion (to download pshb code)
 * bash or similar shell to run the scripts

Installing
----------

::

	git clone https://github.com/marianoguerra/pshb-example.git
	cd pshb-example
	bash setup.sh

the first command will fetch the project from github, the third one will get some
libraries needed for the example to run.

note: answer "y" to sammy and "n" to all the other questions that the script
does (we don't need those libraries)

Running
-------

now we will start the example application called pleinu twice (so we can test the communication
using the hub) and we will start a local pshb hub.

open 3 terminals and run one comment on each one::

	google_appengine/dev_appserver.py src/ -p 8000 --datastore_path=/tmp/tubes1
	google_appengine/dev_appserver.py src/ -p 8001 --datastore_path=/tmp/tubes2
	google_appengine/dev_appserver.py pubsubhubbub/hub/

this commands asume that you are at the root of the pshb-example folder.

Playing
-------

open a browser tabs pointing to:

 * http://localhost:8000/

click the signup link and create a new user, I will create one called spongebob, you will have
to change the username whenever you see it.

after the signup process click the login button and enter the user and password you just entered.

create a message and click send, the message should appear below.

now go to http://localhost:8000/atom/messages/from/spongebob/

you should see an atom feed with the message you just created.

Publishing
----------

now that we have a page that generates information we need to publish it on the hub.

open a tab in your browser pointing to http://localhost:8080/ and click on the publish link near the bottom.

if you get an error remove the s from the https protocol in the address bar and refresh.

on the Topic field enter the url to the atom feed we saw before: http://localhost:8000/atom/messages/from/spongebob/

and click Publish, the page wont change, that's ok.

Subscribing
-----------

now we need to subscribe one user from the other site (http://localhost:8001/) to the messages sent by our user.

go to http://localhost:8001/ and create another user, I will call it patrick

in the main page of the hub (http://localhost:8080/) click on the subscribe like near the bottom

enter http://localhost:8001/p/notify/patrick/ on the Callback field (change patrick for your username if you used another one)
enter http://localhost:8000/atom/messages/from/spongebob/ on the Topic field (change spongebob for your username if you used another one)

click the "Do it" button, the page won't change, that's ok.

Sending a message
-----------------

Go to http://localhost:8000/ (login if you closed it) and send a message.

Now go to http://localhost:8001/ and refresh the page, you should see the messages published by the user in the other site.

..note:: to make it work and avoid an exception I had to add a return statement at the beginning of the log_message function at google_appengine/google/appengine/tools/dev_appserver.py

if you get that exception like this::

        in log_request
            self.requestline, str(code), str(size))
          File "/home/asd/pubsubhubbub/pshb/google_appengine/google/appengine/
        tools/dev_appserver.py", line 3314, in log_message
            if self.channel_poll_path_re.match(self.path):
        AttributeError: DevAppServerRequestHandler instance has no attribute
        'path' 

edit the function to look like this::

    def log_message(self, format, *args):
      """Redirect log messages through the logging module."""
      return
      if self.channel_poll_path_re.match(self.path):
        logging.debug(format, *args)
      else:
        logging.info(format, *args)

you will have to set write permissions to the file to save it (chmod u+w dev_appserver.py)

