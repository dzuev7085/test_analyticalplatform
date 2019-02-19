"""This module runs the Mattermost integration standalone"""
import environ

from integrations.mattermost.utils.post_message import post_message

env = environ.Env()
ROOT_DIR = environ.Path(__file__) - 4  #
env.read_env(str(ROOT_DIR.path('.env')))

MATTERMOST_WEBHOOK = env.str('MATTERMOST_WEBHOOK', False)

post_message(MATTERMOST_WEBHOOK,
             'github',
             'Testing the channel :crocodile:')
