$(function () {
  var stateToColor = {
    'unscheduled': 'white',
    'accepted': 'green',
    'unstarted': 'white',
    'delivered': 'orange',
    'started': 'blue',
    'finished': 'blueDark',
    'rejected': 'red'
  };

  var Story = Backbone.Model.extend({
    defaults: {
      "story_type": "",
      "name": "",
      "labels": [],
      "current_state": "",
      "requested_by": "",
      "owned_by": "",
      "estimate": "",
      "id": "",
      "show": true
    }
  });

  var StoryList = Backbone.Collection.extend({
    model: Story,
    url: "/api/story/",
    allStates: ['unscheduled', 'accepted', 'unstarted', 'delivered', 'started', 'finished', 'rejected'],
    parse: function (json) {
      return json.objects;
    },

    getStoryByType: function (type) {
      return this.where({current_state: type})
    },

    filterByState: function (type) {
      var filteredStories = this.getStoryByType(type);
      _.each(filteredStories, function (story) {
        story.attributes.show = !story.attributes.show;
      });
    },

    getCountByState: function (type) {
      return this.getStoryByType(type).length;
    }
  });

  var CurrentStoryList = Backbone.Collection.extend({
    model: Story,
    url: "/api/current/",
    parse: function (json) {
      return json.objects;
    },
    getStoryByType: function (type) {
      return this.where({story_type: type})
    }
  });

  var StoryView = Backbone.View.extend({
    template: _.template($('#story-item').html()),
    tagName: 'div',
    className: "tile",
    render: function () {
      var model_json = this.model.toJSON();

      $(this.el).html(this.template(this.model.toJSON()));
      $(this.el).addClass('bg-color-' + stateToColor[this.model.attributes.current_state]);

      if (!model_json.show)
        $(this.el).hide();
      return this;
    }
  });

  var StoryListView = Backbone.View.extend({
    el: $('#current>ul'),
    events: {
      'click button.story-switch': 'handleStatus'
    },

    initialize: function () {
      var self = this;
      this.stories = new CurrentStoryList();
      this.stories.fetch({success: function () {
        self.render();
      }});
      _.bindAll(this, 'handleStatus');
    },

    render: function () {
      var $el = $(this.el);
      _.each(this.stories.allStates, function (state) {
        $('button.' + state).html(state + ' - ' + this.stories.getCountByState(state));
      }, this);

//      $el.find('tbody').html('');
      _.each(this.stories.models, function (story) {
        $el.append(new StoryView({model: story}).render().el);
      }, this);

    }
  });

  var CurrentStoryListView = Backbone.View.extend({
    el: $('#current>div'),
    events: {
      'click button.story-switch': 'handleStatus'
    },

    initialize: function () {
      var self = this;
      this.stories = new CurrentStoryList();
      this.stories.fetch({success: function () {
        self.render();
      }});
      _.bindAll(this, 'handleStatus');
    },

    handleStatus: function (ev) {
      var button = $(ev.target);
      this.stories.filterByState(button.attr('data-type'));
      if (button.hasClass("on"))
        button.removeClass("on").addClass("off");
      else
        button.removeClass("off").addClass("on");
      this.render();
    },

    render: function () {
      var $el = $(this.el)
        , featured = this.stories.getStoryByType('feature')
        , modelLength = Math.floor(featured.length / 3)
        , length
        , arrayFull = []
        , array
        , shuffle = function (array) {
          var tmp, current, top = array.length;

          if (top) while (--top) {
            current = Math.floor(Math.random() * (top + 1));
            tmp = array[current];
            array[current] = array[top];
            array[top] = tmp;
          }

          return array;
        };


      _.each(featured, function (story, i) {
        var $element = new StoryView({model: story}).render().el;
        $el.append($element);

        if (i % modelLength == 0 && i > 0)
          $el.append($('<br>'));

        arrayFull.push($element);
      }, this);

      // copy the arrayFull in the array
      array = shuffle(arrayFull.slice(0));

      // animation
      setInterval(function () {
        var element = array.pop();

        $('.tile-magic.visible').toggleClass('visible');
        $(element).find('.tile-magic').toggleClass('visible');

        if (array.length === 0)
          array = shuffle(arrayFull.slice(0));

      }, 2000);
    }
  });


  // generic widget, extend this and customize render
  // with right model
  var GenericWidget = Backbone.View.extend({
    tagName: 'li',
    sizeX: 1,
    sizeY: 1,
    row: 1,
    col: 1
  });

  var EpicsWidget = GenericWidget.extend({
    render: function () {
      $(this.el).html('Epics');
      return this;
    }
  });

  var GridsterWafwfyApp = Backbone.View.extend({
    el: $(".gridster ul"),
    widgets: [
      EpicsWidget
    ],
    gridster: null,
    initialize: function () {
      this.gridster = $(this.el).gridster({
        widget_margins: [10, 10],
        widget_base_dimensions: [140, 140]
      }).data('gridster');
      this.render();
    },
    render: function () {
      _.each(this.widgets, function (Widget) {
        var widget = new Widget();
        this.gridster.add_widget(widget.render().el,
          widget.sizeX, widget.sizeY);
      }, this)
    }
  });

  var MetroUIWafwfyApp = Backbone.View.extend({
    el: $(".gridster ul"),
    widgets: [
      EpicsWidget
    ],
    gridster: null,
    initialize: function () {
      $("body").metroUI();
      this.render();
    },
    render: function () {
      _.each(this.widgets, function (Widget) {
//        var widget = new Widget();
//        this.gridster.add_widget(widget.render().el,
//          widget.sizeX, widget.sizeY);
      }, this)
    }
  });

  window.wafwfyApp = new MetroUIWafwfyApp;
  window.currentStoryList = new CurrentStoryListView;
});

$(function () {
  var chart;
  $(document).ready(function () {
    $.get('/api/velocity/last/5/').done(function (data) {
      new Highcharts.Chart({
        chart: {
          renderTo: 'velocity-chart',
          type: 'column',
          margin: [ 0, 0, 0, 0],
          backgroundColor: 'transparent'
        },
        colors: [
          '#ffffff'
        ],
        title: {
          text: null
        },
        xAxis: {
          labels: {
            enabled: false
          }
        },
        yAxis: {
          labels: {
            enabled: false
          },
          gridLineColor: 'transparent'
        },
        legend: {
          enabled: false
        },
        tooltip: {
          enabled: false
        },
        series: [
          {
            name: 'Velocity',
            data: data.object
          }
        ],
        credits: {
          enabled: false
        }
      });
    });


    chart = new Highcharts.Chart({
      chart: {
        renderTo: 'tags-chart',
        type: 'bar',
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
        formatter: function () {
          return '' +
            this.series.name + ': ' + this.y + '';
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
      series: [
        {
          name: 'unscheduled',
          data: []
        },
        {
          name: 'scheduled',
          data: []
        },
        {
          name: 'finished',
          data: []
        }
      ]
    });

    // anything not in this is supposed to be 1.
    var state_to_series = {
      'unscheduled': 0,
      'finished': 2
    };
    $.get('/api/epics/').done(function(data) {
      for (var key in data['objects']) {
        for (var state in data['objects'][key]) {
          console.log(key, state, data['objects'][key][state]);
          var series = state_to_series[state];
          if (series === undefined)
            series = 1;
          chart.series[series].addPoint([key, data['objects'][key][state]])
        }
      }
    });
    // series[#typeofstory].addPoint([#epic, #story])
//    chart.series[0].addPoint([0, 1])
//    chart.series[1].addPoint([0, 2])
//    chart.series[0].addPoint([1, 10])

  });
});
