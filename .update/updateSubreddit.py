# Hi, if you're modifying this file to run yourself you should change the user agent, thanks.

import praw, os, re
from csscompressor import compress

# Read config from environment variables
client_id = os.environ['REDDIT_CLIENT_ID']
client_secret = os.environ['REDDIT_CLIENT_SECRET']
username = os.environ['REDDIT_USERNAME']
password = os.environ['REDDIT_PASSWORD']
try:
    sub_name = sys.argv[1]
except Exception:
    sub_name = os.environ['REDDIT_SUBREDDIT']
try:
    skip_minify = not os.environ['REDDIT_SKIP_MINIFY'].lower() in ['0', 'false']
except Exception:
    skip_minify = False

if not client_id or not client_secret:
    raise ValueError("Missing Reddit app credentials. Make sure you set the REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables in your Travis settings.")
if not username or not password:
    raise ValueError("Missing Reddit user authentication. Make sure you set the REDDIT_USERNAME and REDDIT_PASSWORD environment variables in your Travis settings.")
if not sub_name:
    raise ValueError("Missing target subreddit. Make sure you set the REDDIT_SUBREDDIT environment variable in your Travis settings, or pass a subreddit name as an argument to the script. Note that this sub's theme will be overwritten.")

# Reddit init and login stuff
# scopes = ["wikiedit", "modconfig"]
r = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    username=username,
    password=password,
    user_agent="script:geo1088/reddit-stylesheet-sync:v1.0 (written by /u/geo1088; run by /u/{})".format(username))
print("Logged into Reddit as /u/{}".format(username))

# Read stylesheet
with open(os.path.join(os.getcwd(), "style.css"), "r") as stylesheet_file:
    stylesheet = stylesheet_file.read()
print("Got stylesheet.")

# Strip leading @charset (Reddit doesn't allow it but Sass adds it sometimes)
stylesheet = re.sub(r"^@charset.*\n", "", stylesheet)

# Minify if we should
if skip_minify:
    print("Skipping minification.")
else:
    stylesheet = compress(stylesheet)
    print("Minified stylesheet.")

# Print the thing because I'm sick of your shit
print("\n\n=== stylesheet ===")
print(stylesheet)
print("=== /stylesheet ===")

# Push the stylesheet to the subreddit
print("Writing stylesheet to /r/{}".format(sub_name))
sub = r.subreddit(sub_name)
try:
    edit_msg = "https://github.com/{}/compare/{}".format(
        os.environ['TRAVIS_REPO_SLUG'],
        os.environ['TRAVIS_COMMIT_RANGE'])
    sub.wiki['config/stylesheet'].edit(stylesheet, edit_msg)
except Exception as e:
    print("Ran into an error while uploading stylesheet; aborting.")
    raise e

print("That's a wrap!")

# TODO: Get and upload the sidebar

# sidebar = open(os.path.join(os.path.join(dir, os.pardir), "sidebar.md"))
# sidebarContents = sidebar.read()
# sidebar.close()
# sub.edit_wiki_page("config/sidebar", sidebarContents, updateReason)