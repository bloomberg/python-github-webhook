Welcome to python-github-webhook's documentation!
=================================================

Very simple, but powerful, microframework for writing Github webhooks in Python.

.. code-block:: python

  from github_webhook import Webhook
  from flask import Flask
  
  app = Flask(__name__)  # Standard Flask app
  webhook = Webhook(app) # Defines '/postreceive' endpoint
  
  @app.route("/")        # Standard Flask endpoint
  def hello_world():
      return "Hello, World!"
  
  @webhook.hook()        # Defines a handler for the 'push' event
  def on_push(data):
      print("Got push with: {0}".format(data))
  
  if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

Contents:

.. toctree::
   :maxdepth: 1

   api_reference
   references
