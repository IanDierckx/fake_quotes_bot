from random import randrange

import praw
import re
import os

def import_quotes():
    with open("quotes.txt") as file:
        quotes = file.read()
        quotes = quotes.split("\n")
        quotes = list(filter(None, quotes))
        return quotes

def import_quoters():
    with open("quoters.txt") as file:
        quoters = file.read()
        quoters = quoters.split("\n")
        quoters = list(filter(None, quoters))
        return quoters


def get_random_quote(quotes, quoters):
    quote = quotes[randrange(len(quotes))]
    quote += " - "
    quote += quoters[randrange(len(quoters))]
    return quote

def run_bot():
    reddit = praw.Reddit('bot1')

    subreddit = reddit.subreddit("BotTestingPlace")

    quotes = import_quotes()
    quoters = import_quoters()

    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt") as file:
            posts_replied_to = file.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    for submission in subreddit.new(limit=10):
        for comment in submission.comments:
            if comment.id not in posts_replied_to:
                if re.search("[\"\'][\w \.]*[\"\'] - [\w \.]*", comment.body, re.IGNORECASE):
                    randomQuote = get_random_quote(quotes, quoters)
                    comment.reply(randomQuote)
                    print("Bot replying to comment: ", comment.body, "by ", comment.author, " with ", randomQuote)
                    posts_replied_to.append(comment.id)
        if submission.id not in posts_replied_to:
            if re.search("[\"\'][\w \.]*[\"\'] - [\w \.]*", submission.title, re.IGNORECASE):
                reply = submission.reply("\"Fake Quote on post.\" - Mrs. Test")
                print("Bot replying to post: ", submission.title, "by ", submission.author, " with ", randomQuote)
                posts_replied_to.append(submission.id)
                posts_replied_to.append(reply.id)

    with open("posts_replied_to.txt", "w") as file:
        for post_id in posts_replied_to:
            file.write(post_id + "\n")


if __name__ == '__main__':
    run_bot()
