#from dolt.apis.github import GitHub
import jinja2
import json
import os
import re
from xml.sax.saxutils import escape
import requests
BASE_PATH = os.path.dirname(__file__)

def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')
CONFIG = json.load(open(os.path.join(BASE_PATH, "config.json")))
templates = jinja2.Environment(loader=jinja2.FileSystemLoader(
    os.path.join(BASE_PATH, 'templates')
),autoescape=guess_autoescape,extensions=['jinja2.ext.autoescape'])

GITHUB_API = 'https://github.com/api/v2/json/'

def grab_open_issues(github_repo, requests_session):
    url = GITHUB_API + 'issues/list/%s/%s/open' % (CONFIG['github_org'], github_repo)
    return requests_session.get(url).content

def display_github_issues(environ, start_response):
    # pass through the basic auth header
    requests_session = requests.session(headers={'Authorization':environ['HTTP_AUTHORIZATION']})
    # parse the repo from the path
    github_repo = environ['PATH_INFO'][1:] # strip the leading /
    if github_repo.endswith('/'):          # string the trailing /
        github_repo = github_repo[0:-1]
    template = templates.get_template("pivotal.xml")
    start_response("200", [('Content-Type', 'application/xml')])
    resp = grab_open_issues(github_repo, requests_session)
    issues = json.loads(resp)
    output = template.render({"issues": issues['issues']}) 
    return [output]

def application(environ, start_response):
    result = display_github_issues(environ, start_response)
    return result

##### the rest is for pivotal activity hook, doesn't work yet
#
#CHECK_FOR_GITHUB_REGEX = re.compile("<other_url>http://github.com/%s/%s/issues/\d+</other_url>" % (
#    CONFIG['github_org'], CONFIG['github_repo']))
#OTHER_ID_REGEX = re.compile("<other_id>(\d+)</other_id>")
#EVENT_TYPE_REGEX = re.compile("<event_type>([^<]+)</event_type>")
#UPDATE_TYPE_REGEX = re.compile("<current_state>([^<]+)</current_state>")
#
#def do_issue_label(issue_id, label, action):
#    #gh = GitHub()
#    #req = getattr(getattr(getattr(getattr(getattr(
#    #        gh.issues.label,
#    #        action),
#    #        CONFIG['github_org']),
#    #        CONFIG['github_repo']),
#    #        label),
#    #        issue_id)
#    url = GITHUB_API + 'issues/label/%s/%s/label/%s' % (CONFIG['github_org'], CONFIG['github_repo'], issue_id)
#    return requests.post(url, headers={'authorization':AUTH}).content
#
#def add_label(issue_id, label):
#    return do_issue_label(issue_id, label, 'add')
#
#def remove_label(issue_id, label):
#    return do_issue_label(issue_id, label, 'remove')
#
#def get_issue(id):
#    url = GITHUB_API + 'issues/show/%s/%s/%s' % (CONFIG['github_org'], CONFIG['github_repo'], id)
#    return requests.get(url, headers={'authorization':AUTH}).content
#    #return getattr(getattr(getattr(
#    #    GitHub().issues.show,
#    #    CONFIG['github_org']),
#    #    CONFIG['github_repo']),
#    #    id
#    #)()['issue']
#
#def do_issue(id, type):
#    #return getattr(getattr(getattr(getattr(
#    #    GitHub().issues,
#    #    type),
#    #    CONFIG['github_org']),
#    #    CONFIG['github_repo']),
#    #id).POST(login=CONFIG['github_user'], token=CONFIG['github_apikey'])
#    url = GITHUB_API + 'issues/%s/%s/%s/%s' % (type, CONFIG['github_org'], CONFIG['github_repo'], id)
#    return requests.post(url, headers={'authorization':AUTH}).content
#
#def reopen_issue(id):
#    return do_issue(id, 'reopen')
#
#def close_issue(id):
#    return do_issue(id, 'close')
#
#def update_github(environ, start_response):
#    pivotal = environ['wsgi.input'].tmp.read()
#    matches = OTHER_ID_REGEX.search(pivotal).groups()
#    on_github = CHECK_FOR_GITHUB_REGEX.search(pivotal) != None
#    if len(matches) != 1 or not on_github:
#        start_response("404", [])
#        return []
#
#    issue_id = matches[0]
#    event_type = EVENT_TYPE_REGEX.search(pivotal).groups()[0]
#
#    if event_type == "story_create":
#        add_label(issue_id, 'accepted')
#
#    if event_type == "story_update":
#        current_state = UPDATE_TYPE_REGEX.search(pivotal).groups()[0]
#        if current_state == "finished":
#            add_label(issue_id, "finished")
#        elif current_state == "accepted":
#            close_issue(issue_id)
#        elif current_state == "delivered":
#            pass # do not thing for now
#        else:
#            issue = get_issue(issue_id)
#            if "finished" in issue['labels']:
#                remove_label(issue_id, "finished")
#            if issue['state'] == "closed":
#                reopen_issue(issue_id)
#
#    start_response("202", [])
#    return []
#
#def application(environ, start_response):
#    global AUTH
#    AUTH = environ['HTTP_AUTHORIZATION']
#    if environ['REQUEST_METHOD'] == 'POST':
#        return update_github(environ, start_response)
#    else:
#        result = display_github_issues(environ, start_response)
#        return result
#
