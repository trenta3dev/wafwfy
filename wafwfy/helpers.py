"""
helper classes and methods
"""
import requests

from wafwfy import app, redis


class MissingPivotalConfigurationError(Exception):
    pass


class PivotalRequest(object):
    ROOT = "https://www.pivotaltracker.com/services/v3/"

    def __init__(self):
        self.token = app.config.get('PIVOTAL_TOKEN')
        self.project = app.config.get('PIVOTAL_PROJECT')

        if not self.token or not self.project:
            raise MissingPivotalConfigurationError

    @property
    def project_root(self):
        return "{root}projects/{project_id}/".format(
            root=self.ROOT, project_id=self.project
        )

    def get(self, url):
        response = requests.get(
            url,
            headers={
                'X-TrackerToken': self.token
            }
        )

        return response.content

    def get_all_stories(self):
        from xml.etree import ElementTree as etree

        content = self.get(self.project_root + "stories")

        root = etree.fromstring(content)

        for story_el in root.findall('story'):
            find = story_el.find
            story = dict(
                id=find('id').text,
                name=find('name').text,
                story_type=find('story_type').text,
                current_state=find('current_state').text,
            )

            try:
                story['estimate'] = int(find('estimate').text)
            except AttributeError:
                pass

            try:
                story['labels'] = find('labels').text.split(',')
            except AttributeError:
                print story_el, list(story_el)
                pass

            try:
                story['owned_by'] = find('owned_by').text
            except AttributeError:
                pass

            yield story
