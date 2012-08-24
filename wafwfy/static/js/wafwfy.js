$(function () {
  var Story = Backbone.Model.extend({
    defaults: {
      "story_type": "",
      "name": "",
      "labels": [],
      "current_state": "",
      "owned_by": "",
      "estimate": "",
      "id": ""
    }
  });

  var StoryList = Backbone.Collection.extend({
    model: Story,
    url: "/api/story/",
    parse: function (json) {
      return json.objects;
    }
  });

  var StoryView = Backbone.View.extend({
    template: _.template($('#story-item').html()),
    render: function () {
      $(this.el).html(this.template(this.model.toJSON()));
      return this;
    }
  });

  var StoryListView = Backbone.View.extend({
    el: $("body"),
    initialize: function () {
      var self = this;
      this.model = new StoryList();
      this.model.fetch({success: function () {
        self.render();
      }});
    },
    render: function () {
      var $el = $(this.el);
      _.each(this.model.models, function (story) {
        $el.append(new StoryView({model: story}).render().el);
      }, this);
    }

  });

  new StoryListView;
});