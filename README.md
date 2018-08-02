# PCO-oauth2


OAuth v2.0 Planning Center Online Example using 
[kennethreitz](https://github.com/kennethreitz)'s well-known
[Requests](https://github.com/kennethreitz/requests) library.
This is a slightly modified version of [Miguel Araujo's](https://github.com/maraujop/requests-oauth2)
requests-oauth2. 

This library provides a demonstration of authenticating with 
Planning Center Online using Oauth 2.0 in Python

Authors: see [AUTHORS](/AUTHORS).

License: BSD

Example: with [Flask](/examples/web_flask.py).

## OAuth2 web app flow - the theory

Skip this if you know how OAuth2 works.

1. Your web app (*Foo*) allows users to log in with their *Planning Center Online(PCO)*
   account. *Planning Center Online* gave you a **client
   ID** and a **secret key**, which *Foo* stores somewhere on the
   backend. *PCO* and *Foo* pre-agree on some **redirect URI**.
2. User visits *Foo*'s login screen, e.g.
   `https://www.foo.example/login`
3. *Foo* redirects users to *Qux*'s **Authorization URL**, e.g.
   `https://api.planningcenteronline.com/oauth/authorize`
4. User is presented with *PCO*'s **consent screen**, where they
   review the **scope** of requested permissions, and either allow or
   deny access.
5. Once access is granted, *PCO* redirects back to *Foo* via the
   **redirect URI** that they both agreed upon beforehand, supplying
   the **code**.
6. *Foo* exchanges the **code** for an **access token**. The access
   token can be used by *Foo* to make API calls to *PCO* on user's
   behalf.

## Usage example

Look into the [examples directory](/examples) for a fully integrated,
working example.

You will find **Client ID** & **secret** (point 1 above) in
[My Developer Applications](https://api.planningcenteronline.com/oauth/applications).

You must choose the **redirect URI**, which must be handled by your
web app. For the example to work you need to add http://localhost:5000

```python
import os
from requests_oauth2.services import PlanningCenterClient
# You need to put your Client ID and Secret in environment variables PCO_CLIENT_ID & PCO_CLIENT_SECRET respectively
app.client_id = os.environ["PCO_CLIENT_ID"]
app.secret_key = os.environ["PCO_CLIENT_SECRET"]
pco_auth = PlanningCenterClient(
    client_id=app.client_id, 
    client_secret=app.secret_key,
    redirect_uri='http://localhost:5000/auth/callback'
)
```

When the user visits the login page (point 2), we'll build an
**authorization URL** (point 3) that will direct the user to PCO's
**consent screen**, asking to grant the specified **scopes** (point
4):

```python
authorization_url = pco_auth.authorize_url(
    scope=["people", "services", "check_ins", "resources"],
    response_type="code",
)
```

Once the user clicks "allow", PCO will redirect them to the
**redirect URI** (point 5), which will include the **code** as one of
the query string parameters:

    http://localhost:5000/pco/oauth2callback?code=...

The code will be used to request an **access token** (point 6),
necessary for all following requests to the API:

```python
code = get_request_parameter("code")  # this depends on your web framework!
data = pco_auth.get_token(
    code=code,
    grant_type="authorization_code",
)
```

You can store it somewhere for later use, e.g. in the session, or in
the database:

```python
session["access_token"] = data["access_token"]
```

The exact method for supplying the **access token** varies from one
provider to another. One popular method (supported by PCO) is via
the Bearer header. There's a helper shortcut for this:

```python
from requests_oauth2 import OAuth2BearerToken

with requests.Session() as s:
    s.auth = OAuth2BearerToken(access_token)
    r = s.get("https://api.planningcenteronline.com/people/v2/people")
    r.raise_for_status()
    data = r.json()
```

## Interesting readings

* Using OAuth 2.0 to Access Google APIs:
  <https://developers.google.com/accounts/docs/OAuth2>

* Using OAuth 2.0 for Web Server Applications Google APIs:
  <https://developers.google.com/accounts/docs/OAuth2WebServer>

* OAuth 2.0 in Facebook:
  <http://developers.facebook.com/docs/authentication/>

* Github OAuth 2.0 usage:
  <https://developer.github.com/apps/building-oauth-apps/>

* You can use postbin for testing webhooks: <http://www.postbin.org/>
