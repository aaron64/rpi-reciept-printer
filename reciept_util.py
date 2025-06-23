import emoji

def filter_emojis(string):
    return emoji.replace_emoji(string, replace='')
