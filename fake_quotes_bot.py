import praw
import pdb
import re
import os


def run_bot():
    reddit = praw.Reddit('bot1')

    subreddit = reddit.subreddit("BotTestingPlace")

    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt") as file:
            posts_replied_to = file.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    for submission in subreddit.new(limit=10):
        if submission.id not in posts_replied_to:
            if re.search("[\"\'][\w \.]*[\"\'] - [\w \.]*", submission.title, re.IGNORECASE):
                submission.reply("\"Fake Quote\" - Mrs. Test")
                print("Bot replying to : ", submission.title)
                posts_replied_to.append(submission.id)

    with open("posts_replied_to.txt", "w") as file:
        for post_id in posts_replied_to:
            file.write(post_id + "\n")

if __name__ == '__main__':
    run_bot()
