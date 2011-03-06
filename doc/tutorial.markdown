= PubHubSubBub Developer Tutorial =

welcome, this document contains an example application written in python
that will help you play with a pshb (pubsubhubbub from now on) hub and
an application that publishes its content to it.

== Requirements ==

* python >= 2.5 (I'm using 2.6.1)
* git (for the example)
* subversion (to download pshb code)
* bash or similar shell to run the scripts

== Installing ==

{{{
git clone https://github.com/marianoguerra/pshb-example.git
cd pshb-example
bash build.sh
}}}

the first command will fetch the project from github, the third one will get some
libraries needed for the example to run.

note: answer "n" to all the questions that the script does (we don't need those libraries)

== Running ==

now we will start the example aplication called pleinu twice (so we can test the comunication
using the hub) and we will start a local pshb hub.

open 3 terminals and run one comment on each one

{{{
google_appengine/dev_appserver.py src/ -p 8000 --datastore_path=/tmp/tubes1
google_appengine/dev_appserver.py src/ -p 8001 --datastore_path=/tmp/tubes2
google_appengine/dev_appserver.py pubsubhubbub/hub/
}}}

this commands asume that you are at the root of the pshb-example folder.

== Playing ==

open a browser tabs pointing to:

 * http://localhost:8000/

click the signup link and create a new user, I will create one called spongebob, you will have
to change the username whenever you see it.

after the signup process click the login button and enter the user and password you just entered.

create a message and click send, the message should appear below.

now go to http://localhost:8001/atom/messages/from/spongebob/

you should see an atom feed with the message you just created.

== Publishing ==

now that we have a page that generates information we need to publish it on the hub.

open a tab in your browser pointing to http://localhost:8080/ and click on the publish link near the bottom.

if you get an error remove the s from the https protocol in the address bar and refresh.

on the Topic field enter the url to the atom feed we saw before: http://localhost:8001/atom/messages/from/spongebob/

and click Publish, the page wont change, that's ok.

== Subscribing ==

now we need to subscribe one user from the other site (http://localhost:8080/) to the messages sent by our user.

in the main page of the hub (http://localhost:8080/) click on the subscribe like near the bottom


