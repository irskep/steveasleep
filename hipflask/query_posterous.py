import logging
import simplejson
import posterous
import re

from google.appengine.api import memcache

import settings

encode_posts = simplejson.dumps
decode_posts = simplejson.loads

from models import RecentPosts

firstPar = re.compile(r"^(?P<first><p>.*</p>).*")

def delete_all(ModelClass):
    objs = ModelClass.all()
    for obj in objs:
        obj.delete()

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
                logging.info('no match')
                return post.body
        posts = [{
            'title': post.title,
            'link': post.link,
            'body': first_par_for_post(post),
            'date': post.date.strftime("%B %d, %Y")
            
        } for post in posts_repr]
        logging.info(str(posts))
        logging.info(str(encode_posts(posts)))
        
        delete_all(RecentPosts)
        RecentPosts(postsJson=encode_posts(posts)).put()
        
        return posts
    else:
        logging.info('No primary posterous site')
        return {}

def get_posts():
    posts = memcache.get("posts")
    if posts is not None:
        return posts
    else:
        try:
            posts = decode_posts(RecentPosts.all()[0].postsJson)
            memcache.set("posts", posts)
        except IndexError:
            posts = update_posterous()
    
    return posts
