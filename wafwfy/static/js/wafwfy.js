$(function () {
  var Story = Backbone.Model.extend({
    defaults: {
      "story_type": "",
      "name": "",
      "labels": [],
      "current_state": "",
      "owned_by": "",
      "estimate": "",
      "id": "",
      "show": true
    }
  });

  var StoryList = Backbone.Collection.extend({
    model: Story,
    url: "/api/story/",
    parse: function (json) {
      return json.objects;
    },
    getAcceptedStory: function() {
      return this.where({current_state: "accepted"})
    },
    filterByState: function(type){
      var filteredStories = this.where({current_state: type});
      _.each(filteredStories, function(story){
        story.attributes.show = !story.attributes.show;
      });
    }
  });

  var StoryView = Backbone.View.extend({
    template: _.template($('#story-item').html()),
    tagName: 'tr',
    render: function () {
      var model_json = this.model.toJSON();

      $(this.el).html(this.template(this.model.toJSON()));

      switch(model_json.current_state){
        case 'unscheduled':
          $(this.el).css('color','DodgerBlue');
          break;
        case 'accepted':
          $(this.el).css('color', 'LimeGreen');
          break;
        case 'unstarted':
          $(this.el).css('color', 'LightCoral');
          break;
        case 'delivered':
          $(this.el).css('color', 'Orange');
          break;
        case 'started':
          $(this.el).css('color', 'MediumVioletRed');
          break;
        case 'finished':
          $(this.el).css('color', 'Peru');
          break;
      }
      if(!model_json.show)
        $(this.el).hide();
      return this;
    }
  });

  var StoryListView = Backbone.View.extend({
    el: $('table#story-table'),
    events: {
      'click button.story-switch': 'handleStatus'
    },

    initialize: function () {
      var self = this;
      this.stories = new StoryList();
      this.stories.fetch({success: function () {
        self.render();
      }});
      _.bindAll(this, 'handleStatus');
    },

    handleStatus: function(ev){
      var button = $(ev.target);
      this.stories.filterByState(button.attr('data-type'));
      if(button.hasClass("on"))
        button.removeClass("on").addClass("off");
      else
        button.removeClass("off").addClass("on");
      this.render();
    },

    render: function () {
      var $el = $(this.el);
      $el.find('tbody').html('');
      _.each(this.stories.models, function (story) {
        $el.append(new StoryView({model: story}).render().el);
      }, this);
    }

  });

  window.storyList = new StoryListView;
});