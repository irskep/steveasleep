import logging
import simplejson
import string

from google.appengine.api.urlfetch import DownloadError
from google.appengine.api import memcache

from datetime import datetime
from github2.client import Github

import settings

from models import RecentCommits
from queryutil import memcache_or_db_or_web, delete_all

encode_commits = simplejson.dumps
decode_commits = simplejson.loads

def update_github():
    logging.info("updating github")
    github = Github(username=settings.GITHUB_USER, api_token=settings.GITHUB_API_KEY)
    commits = []
    recent_commits = []
    try:
        for r in github.repos.list(for_user=settings.GITHUB_USER):
            new_commits = github.commits.list("%s/%s" % (settings.GITHUB_USER, r.name), 'master')
            for c in new_commits:
                c.repo = r
            commits.extend(new_commits)
        all_commits = sorted(commits, key=lambda c: c.committed_date)
        commits = reversed(all_commits[-settings.NUM_GITHUB_COMMITS:])
        
        linebreak_message = lambda m: string.replace(m, 'github.com/', 'github.com/ ')
        
        for c in commits:
            minute = str(c.committed_date.minute)
            if len(minute) < 2:
                minute = "0" + minute
            recent_commits.append({
                'repo_name': c.repo.name,
                'repo_url': c.repo.url,
                'time': {
                    'day': c.committed_date.day,
                    'month': c.committed_date.month,
                    'year': c.committed_date.year,
                    'hour': c.committed_date.hour,
                    'minute': minute
                },
                'message': linebreak_message(c.message),
                'url': c.url
            })
        
        delete_all(RecentCommits)
        RecentCommits(commitsJson=encode_commits(recent_commits)).put()
        memcache.delete("commits")
    except DownloadError:
        # Some query to Github took too long
        logging.info("unable to download from github")
    
    return recent_commits

get_commits = memcache_or_db_or_web(
    "commits", 
    lambda: decode_commits(RecentCommits.all()[0].commitsJson), 
    update_github
)
