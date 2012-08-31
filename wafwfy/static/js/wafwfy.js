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
    allStates: ['unscheduled','accepted','unstarted','delivered','started', 'finished'],
    parse: function (json) {
      return json.objects;
    },

    getStoryByType: function(type) {
      return this.where({current_state: type})
    },

    filterByState: function(type){
      var filteredStories = this.getStoryByType(type);
      _.each(filteredStories, function(story){
        story.attributes.show = !story.attributes.show;
      });
    },

    getCountByState: function(type){
      return this.getStoryByType(type).length;
    }
  });

  var StoryView = Backbone.View.extend({
    template: _.template($('#story-item').html()),
    tagName: 'tr',
    render: function () {
      var model_json = this.model.toJSON();

      $(this.el).html(this.template(this.model.toJSON()));

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
      _.each(this.stories.allStates, function(state){
          $('button.'+state).html(state + ' - ' + this.stories.getCountByState(state));
      }, this);

      $el.find('tbody').html('');
      _.each(this.stories.models, function (story) {
        $el.append(new StoryView({model: story}).render().el);
      }, this);

    }

  });

  window.storyList = new StoryListView;
});








$(function () {

  var chart;
  $(document).ready(function() {
      chart = new Highcharts.Chart({
          chart: {
              renderTo: 'tags-chart',
              type: 'bar'
          },
          title: {
              text: 'Epics'
          },
          xAxis: {
//              categories: ['Apples', 'Oranges', 'Pears', 'Grapes', 'Bananas']
              categories: epics
          },
          yAxis: {
              min: 0
          },
          legend: {
            enabled: false
          },
          tooltip: {
              formatter: function() {
                  return ''+
                      this.series.name +': '+ this.y +'';
              }
          },
          plotOptions: {
              series: {
                  stacking: 'normal'
              }
          },
//          series: [{
//              name: 'John',
//              data: [5, 3, 4, 7, 2]
//          }, {
//              name: 'Jane',
//              data: [2, 2, 3, 2, 1]
//          }, {
//              name: 'Joe',
//              data: [3, 4, 4, 2, 5]
//          }],
          series: [{
            name: 'aa',
            data: []
          }, {
            name: 'bb',
            data: []
          }]
      });

      console.log(c=chart)
      chart.series[0].addPoint([0, 1])
      chart.series[1].addPoint([0, 2])
      chart.series[0].addPoint([1, 10])

  });
});
