from difflib import ndiff
from aiohttp import ClientSession
from tabulate import tabulate
from fuzzywuzzy import fuzz
from random import randint
from html.parser import HTMLParser


async def evaluate(ctx, a_string: str, b_string: str, time_taken, dm_id):
    """ Returns None on personal event, returns [time_taken,wpm,mistakes] on speedevents"""
    user_obj = ctx.guild.get_member(dm_id) if dm_id else ctx.author
    special_send = user_obj.send if dm_id else ctx.send
    # TODO
    if "​" in b_string:
        if not dm_id:
            await special_send("Imagine cheating bruh, c'mon atleast be honest here.")
        else:
            await special_send("You cheated and hence you are disqualified.")
        return
    else:
        mistakes = 0
        for i, s in enumerate(ndiff(a_string, b_string)):
            if s[0] == " ":
                continue
            elif s[0] == "-" or s[0] == "+":
                mistakes += 1
    # Analysis
    accuracy = fuzz.ratio(a_string, b_string)
    wpm = len(a_string) / 5 / (time_taken / 60)
    if accuracy > 66:  # TODO add to config
        verdict = [
            (
                "WPM (Correct Words per minute)",
                wpm - (mistakes / (time_taken / 60)),
            ),
            ("Raw WPM (Without accounting mistakes)", wpm),
            ("Accuracy(Levenshtein)", accuracy),
            ("Words Given", len(a_string.split())),
            (f"Words from {user_obj.display_name}", len(b_string.split())),
            ("Characters Given", len(a_string)),
            (f"Characters from {user_obj.display_name}", len(b_string)),
            (f"Mistakes done by {user_obj.display_name}", mistakes),
        ]
        await special_send(content="```" + tabulate(verdict, tablefmt="fancy_grid") + "```")
        return [time_taken, wpm - (mistakes / (time_taken / 60)), mistakes]
    else:
        await special_send(
            f"{'You' if dm_id else user_obj.display_name}  didn't want to complete the challenge."
        )


async def get_text(**kwargs) -> tuple:
    """Gets the paragraph for the test"""
    # TODO add customisable length of text and difficuilty
    async with ClientSession() as session:
        async with session.get("http://www.randomtext.me/api/gibberish/p-1/25-45") as f:
            if f.status == 200:
                resp = await f.json()
            else:
                return ("Something went wrong while getting the text", 0)
    cleanup = HTMLFilter()
    cleanup.feed(resp["text_out"])
    a_string = cleanup.text.strip()
    return (a_string, 1)


class HTMLFilter(HTMLParser):
    """For HTML to text properly without any dependencies.
    Credits: https://gist.github.com/ye/050e898fbacdede5a6155da5b3db078d"""

    text = ""

    def handle_data(self, data):
        self.text += data


def nocheats(text: str) -> str:
    """To catch Cheaters upto some extent"""
    text = list(text)
    size = len(text)
    for _ in range(size // 5):
        text.insert(randint(0, size), "​")
    return "".join(text)