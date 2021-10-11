import sys
from random import randrange
import praw
import re
import os

quotes = []
quoters = []


# Function to generate a random fake quote from the imported quotes and quoters
def get_random_quote():
    quote = quotes[randrange(len(quotes))]
    quote += " - "
    quote += quoters[randrange(len(quoters))]
    return quote


# Function to reply to a post (or comment) with a randomly generated fake quote
def reply_to(type_of_post, post, posts_replied_to):
    if type_of_post == "comment":
        text = post.body
    elif type_of_post == "post":
        text = post.title
    elif type_of_post == "mention":
        text = post.body
    else:
        print("Unexpected type of post\n", file=sys.stderr)
        text = ""
    if re.search("[\"\'][\w .?!]*[\"\'] - [\w .?!]*", text, re.IGNORECASE) or \
            (type_of_post == "post" and re.search("[\"\'][\w .?!]*[\"\'] - [\w .?!]*", post.selftext, re.IGNORECASE)) or \
            (type_of_post == "mention"):
        random_quote = get_random_quote()
        reply = post.reply(random_quote
                           + "\n\n This quote is randomly generated and the person quoted will (most likely) never "
                             "have actually said it."
                             "\n\nThis bot was made by u/DarkwoodDragon if you have any notes, please let them know.")
        print("Bot replying to ", type_of_post, ": ", text, "by ", post.author, " with ", random_quote)
        posts_replied_to.append(post.id)
        posts_replied_to.append(reply.id)


# Function will read a file, import the data into a list, remove duplicates and write the duplicate-less list back to
# file while returning the list as well
def import_and_remove_duplicates(filename):
    with open(filename) as file:
        data = file.read()
        data = data.split("\n")
        data = list(set(filter(None, data)))
    with open(filename, "w") as file:
        for line in data:
            file.write(line + "\n")
        return data


def reply_to_comment_and_subcomments(comment, posts_replied_to):
    if comment.id not in posts_replied_to:
        reply_to("comment", comment, posts_replied_to)
    if comment.replies is None:
        return
    else:
        for subcomment in comment.replies.replace_more(limit=None):
            reply_to_comment_and_subcomments(subcomment, posts_replied_to)


# Function that runs the actual bot
def run_bot():
    # Get a reddit instance using the data given in the local praw.ini file. File not added to git to prevent sharing
    # of secret data
    reddit = praw.Reddit('bot1')
    subreddits = import_and_remove_duplicates("subreddits.txt")

    global quotes
    quotes = import_and_remove_duplicates("quotes.txt")
    global quoters
    quoters = import_and_remove_duplicates("quoters.txt")

    # First check if the replied to file already exists or not. If it does import the ids into a list, otherwise make
    # an empty list
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt") as file:
            posts_replied_to = file.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        # Loop over the then newest posts in the subreddit to check for posts and comments to reply to
        for submission in subreddit.new(limit=10):
            for comment in submission.comments.replace_more(limit=None):
                reply_to_comment_and_subcomments(comment, posts_replied_to)
            if submission.id not in posts_replied_to:
                reply_to("post", submission, posts_replied_to)

    for mention in reddit.inbox.mentions(limit=10):
        if mention.id not in posts_replied_to:
            print(f"{mention.author}\n{mention.body}\n")
            reply_to("mention", mention, posts_replied_to)

    # Update the replied to text file to make sure you don't reply again when the bot is run again.
    with open("posts_replied_to.txt", "w") as file:
        for post_id in posts_replied_to:
            file.write(post_id + "\n")


if __name__ == '__main__':
    run_bot()
