"""
helper classes and methods
"""
import requests

from wafwfy import app


class MissingPivotalConfigurationError(Exception):
    pass


def str_to_date(a_string):
    """ convert a string from pivotaltracker into a datetime.
    """
    from datetime import datetime
    from time import mktime, strptime
    from pytz import utc
    return datetime.fromtimestamp(mktime(
        strptime(a_string, "%Y/%m/%d %H:%M:%S UTC")
    )).replace(tzinfo=utc)


def calculate_team_percentages(strength, n_members=5):
    factor = 1. / n_members
    return [min(factor, max(0, strength - factor * i)) / factor * 100
            for i, x in enumerate(range(n_members))]


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
#        return open('stories').read()

        response = requests.get(
            url,
            headers={
                'X-TrackerToken': self.token
            }
        )

        return response.content

    @staticmethod
    def iteration_element_to_dict(iteration_el):
        """ Extract a dictionary representing an iteration
        """
        find = iteration_el.find
        iteration = dict(
            id=find('id').text,
            number=find('number').text,
            stories=find('stories'),
            start=find('start').text,
            finish=find('finish').text,
            team_strength=find('team_strength').text,
        )

        from pytz import utc
        from datetime import datetime
        start_d = str_to_date(iteration['start'])
        end_d = str_to_date(iteration['finish'])
        now = datetime.now().replace(tzinfo=utc)

        if start_d <= now < end_d:
            iteration['current_state'] = 'current'
        elif end_d < now:
            iteration['current_state'] = 'completed'
        else:
            iteration['current_state'] = 'future'

        return iteration


    @staticmethod
    def story_element_to_dict(story_el):
        """
        Extract a dictionary representing a story from an ElementTree element.
        """
        find = story_el.find
        story = dict(
            id=find('id').text,
            name=find('name').text,
            story_type=find('story_type').text,
            current_state=find('current_state').text,
            requested_by=find('requested_by').text,
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

        return story

    def iter_iterations(self):
        from xml.etree import ElementTree as etree

        content = self.get(self.project_root + "iterations")

        root = etree.fromstring(content)

        for story_el in root.findall('iteration'):
            iteration = self.iteration_element_to_dict(story_el)

            yield iteration

    def iter_stories(self, root=None, filter=None):
        if root is None:
            from xml.etree import ElementTree as etree

            filter = '?filter=' + filter if filter else ''
            content = self.get(self.project_root + "stories" + filter)
            root = etree.fromstring(content)

        for story_el in root.findall('story'):
            story = self.story_element_to_dict(story_el)

            yield story

    def iter_icebox(self):
        return self.iter_stories(filter='state:unscheduled')

    def current(self):
        # http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/iterations/current_backlog
        from xml.etree import ElementTree as etree

        content = self.get(self.project_root + "iterations/current")
        root = etree.fromstring(content)
        stories = root.iter('story')
        for story_el in stories:
            story = self.story_element_to_dict(story_el)
            yield story