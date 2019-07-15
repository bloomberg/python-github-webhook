# GitHub Webhook (micro) Framework

[![PyPI](https://img.shields.io/pypi/v/github-webhook.svg)][2]

`python-github-webhook` is a very simple, but powerful, microframework for writing [GitHub
webhooks][1] in Python. It can be used to write webhooks for individual repositories or whole
organisations, and can be used for GitHub.com or GitHub Enterprise installations; in fact, it was
orginally developed for Bloomberg's GHE install.

## Getting started

`python-github-webhook` is designed to be as simple as possible, to make a simple Webhook that
receives push events all it takes is:

```py
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
```

## Advanced Usage:

```
import os
from github_webhook import Webhook
from flask import Flask

app = Flask(__name__)  # Standard Flask app
webhook = Webhook(app, endpoint="/postreceive", secret='postreceivesecret') # Defines '/postreceive' endpoint

@app.route("/")        # Standard Flask endpoint
def hello_world():
    return "Hello, World!"

@webhook.hook()        # Defines a handler for the 'push' event
def on_push(data):
    #print("Got push with: {0}".format(data))
    print(os.popen("sh ~/webhook.sh").read())

if __name__ == "__main__":
    try:
        port_number = int(sys.argv[1])
    except:
        port_number = 8888
    app.run(host="0.0.0.0", port=port_number, debug=False)
```

If code is `webhook = Webhook(app, endpoint="/postreceive", secret='postreceivesecret')` and `port_number = 8888`:
Payload URL settting is resemble: http://yourwebsite:8888/postreceive
Secret settting is `postreceivesecret`

If with no secret setting:
`webhook = Webhook(app, endpoint="/postreceive")`


If code is `webhook = Webhook(app)`:
it'll use default way: `/postreceive`


## License

The `python-github-webhook` repository is distributed under the Apache License (version 2.0);
see the LICENSE file at the top of the source tree for more information.

[1]: https://developer.github.com/webhooks/
[2]: https://pypi.python.org/pypi/github-webhook
