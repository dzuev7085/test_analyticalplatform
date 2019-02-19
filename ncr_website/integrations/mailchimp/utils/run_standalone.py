"""This module runs the Mailchimp integration standalone"""
import environ
from mailchimp3 import MailChimp

env = environ.Env()
ROOT_DIR = environ.Path(__file__) - 4  #
env.read_env(str(ROOT_DIR.path('.env')))

MC_USER = env.str('MC_USER', False)
MC_API_KEY = env.str('MC_API_KEY', False)

client = MailChimp(
    mc_user=MC_USER,
    mc_api=MC_API_KEY,
)

client.campaign_folders.all(get_all=False)
