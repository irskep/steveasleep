from __future__ import with_statement
import logging
import yaml
import copy
from flask import url_for, render_template

apps = {}
reverse_apps = {}
groups = []

with open('content/site.yaml', 'r') as f:
    yaml_repr = yaml.load(f)

for group_repr in yaml_repr:
    group_name = group_repr.keys()[0]
    group_members = group_repr.values()[0]
    items = []
    for item in group_members:
        item_name = item.keys()[0]
        item_url = item.values()[0]
        items.append({'name': item_name, 'url': item_url})
        apps[item_name] = item_url
        reverse_apps[item_url] = item_name
    groups.append({
        'name': group_name,
        'items': items
    })

def parse_groups():
    parsed_groups = [copy.deepcopy(group) for group in groups if group['name'] != 'hidden']
    for group in parsed_groups:
        for item in group['items']:
            if not item['url'].startswith('http'):
                item['url'] = url_for(item['url'])
            logging.info(str(item))
    return parsed_groups

def render_with_app_lists(template, **kwargs):
    kwargs['groups'] = parse_groups()
    return render_template(template, **kwargs)