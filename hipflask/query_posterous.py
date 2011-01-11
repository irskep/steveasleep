import logging
import simplejson
import posterous
import re
from google.appengine.api import memcache
import settings

encode_posts = simplejson.dumps
decode_posts = simplejson.loads

from models import RecentPosts
from queryutil import memcache_or_db_or_web, delete_all

firstPar = re.compile(r"^(?P<first><p>.*</p>).*")

def update_posterous():
    memcache.delete("posts")
    logging.info("updating posterous")
    primary_site = None
    try:
        api = posterous.API(settings.POSTEROUS_USER, settings.POSTEROUS_PASSWORD)
        sites = api.get_sites()
    except Exception, e:
        logging.error('Posterous user information incorrect')
        sites = []
        return {}
    for site in sites:
        if site.primary:
            primary_site = site
    if primary_site:
        posts_repr = primary_site.read_posts()[:settings.NUM_POSTEROUS_POSTS]
        def first_par_for_post(post):
            summary_match = firstPar.match(post.body)
            if summary_match:
                m = summary_match.groups('first')
                if isinstance(m, tuple):
                    return m[0]
                else:
                    return m
            else:
                return post.body
        posts = [{
            'title': post.title,
            'link': post.link,
            'body': first_par_for_post(post),
            'date': post.date.strftime("%B %d, %Y")
            
        } for post in posts_repr]
        
        delete_all(RecentPosts)
        RecentPosts(postsJson=encode_posts(posts)).put()
        
        return posts
    else:
        logging.info('No primary posterous site')
        return {}

get_posts = memcache_or_db_or_web(
    "posts", 
    lambda: decode_posts(RecentPosts.all()[0].postsJson), 
    update_posterous
)
