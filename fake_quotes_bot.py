from random import randrange
import praw
import re
import os


# Function to import fake quotes from external file
def import_quotes():
    with open("quotes.txt") as file:
        quotes = file.read()
        quotes = quotes.split("\n")
        quotes = list(filter(None, quotes))
        return quotes


# Function to import quoters from an external file
def import_quoters():
    with open("quoters.txt") as file:
        quoters = file.read()
        quoters = quoters.split("\n")
        quoters = list(filter(None, quoters))
        return quoters


# Function to generate a random fake quote from the imported quotes and quoters
def get_random_quote(quotes, quoters):
    quote = quotes[randrange(len(quotes))]
    quote += " - "
    quote += quoters[randrange(len(quoters))]
    return quote


# Function that runs the actual bot
def run_bot():
    # Get a reddit instance using the data given in the local praw.ini file. File not added to git to prevent sharing
    # of secret data
    reddit = praw.Reddit('bot1')

    subreddit = reddit.subreddit("BotTestingPlace")

    quotes = import_quotes()
    quoters = import_quoters()

    # First check if the replied to file already exists or not. If it does import the ids into a list, otherwise make
    # an empty list
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt") as file:
            posts_replied_to = file.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    # Loop over the then newest posts in the subreddit to check for posts and comments to reply to
    for submission in subreddit.new(limit=10):
        for comment in submission.comments:
            if comment.id not in posts_replied_to:
                if re.search("[\"\'][\w \.?!]*[\"\'] - [\w \.?!]*", comment.body, re.IGNORECASE):
                    randomQuote = get_random_quote(quotes, quoters)
                    comment.reply(randomQuote)
                    print("Bot replying to comment: ", comment.body, "by ", comment.author, " with ", randomQuote)
                    posts_replied_to.append(comment.id)
        if submission.id not in posts_replied_to:
            if re.search("[\"\'][\w \.?!]*[\"\'] - [\w \.?!]*", submission.title, re.IGNORECASE):
                randomQuote = get_random_quote(quotes, quoters)
                reply = submission.reply(randomQuote)
                print("Bot replying to comment: ", submission.body, "by ", submission.author, " with ", randomQuote)
                posts_replied_to.append(submission.id)
                posts_replied_to.append(reply.id)

    # Update the replied to text file to make sure you don't reply again when the bot is run again.
    with open("posts_replied_to.txt", "w") as file:
        for post_id in posts_replied_to:
            file.write(post_id + "\n")


if __name__ == '__main__':
    run_bot()
