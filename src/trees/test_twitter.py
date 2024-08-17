
# Let's import our OAuth library to setup
from requests_oauthlib.oauth1_auth import Client

# Import requests in order to make server sided requests
import requests


# Create A Config To Store Values
config = {
    'twitter_consumer_key': 'BMUHx2u7N1UlHQwY5AyzwxVvu',
    'twitter_consumer_secret': '03UE6FNNqI80lM74vVg0jk3HVx8ndrK0huvb5PnUSONrqW2rHH'
}

# Initialize Our OAuth Client
oauth = Client(config['twitter_consumer_key'], client_secret=config['twitter_consumer_secret'])


# We have to create our initial endpoint to login with twitter
class TwitterAuthenticate(Resource):
    # Here we are making it so this endpoint accepts GET requests
    def get(self):
        # We must generate our signed OAuth Headers
        uri, headers, body = oauth.sign('https://twitter.com/oauth/request_token')
        # We need to make a request to twitter with the OAuth parameters we just created
        res = requests.get(uri, headers=headers, data=body)
        # This returns a string with OAuth variables we need to parse
        res_split = res.text.split('&') # Splitting between the two params sent back
        oauth_token = res_split[0].split('=')[1] # Pulling our APPS OAuth token from the response.
        # Now we have to redirect to the login URL using our OAuth Token
        return redirect('https://api.twitter.com/oauth/authenticate?oauth_token=' + oauth_token, 302)


# We need to create a parser for that callback URL
def callback_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token')
    parser.add_argument('oauth_verifier')
    return parser


# Now we setup the Resource for the callback
class TwitterCallback(Resource):
    def get(self):
        parser = callback_parser()
        args = parser.parse_args() # Parse our args into a dict
        # We need to make a request to twitter with this callback OAuth token
        res = requests.post('https://api.twitter.com/oauth/access_token?oauth_token=' + args['oauth_token'] + '&oauth_verifier=' + args['oauth_verifier'])
        res_split = res.text.split('&')
        # Now we need to parse our oauth token and secret from the response
        oauth_token = res_split[0].split('=')[1]
        oauth_secret = res_split[1].split('=')[1]
        userid = res_split[2].split('=')[1]
        username = res_split[3].split('=')[1]
        # We now have access to the oauth token, oauth secret, userID, and username of the person who logged in.
        # .... Do more code here
        # ....
        return redirect('http://localhost:3000', 302)


