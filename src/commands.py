"""
Lists of possible commands to activate functions
"""

#spotify music from user - only activated by "play" for now
user_music = ["play"]

#activation for friday-suggested music
friday_music = ["play me some music", "play some music", "give me some music", "put something on", "music please"]

#activation to get weather info
weather_info = ["forecast", "weather"]

#sending a reminder
reminder_send = ["remind me", "reminder", "notify me", "message me", "send me"]

#sending a message to girlfriend
message_send = ["send sophie", "message sophie", "notify sophie", "remind sophie", "let sophie know"]

#send friday to sleep-mode
start_sleep = ["that's all", "that is all", "goodbye", "see you later", "we'll talk soon"]


def find_match(commands, query):
    """Algorithm to match commands with response"""
    for command in commands:
        if command in query.lower():
            return True
    return False

