ANIMATION_DELAY = 15000;
ANIMATION_SPEED = 1000;
STORY_ANIMATION_DELAY = 3000;

var getParameterByName = function (name)
{
  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
  var regexS = "[\\?&]" + name + "=?([^&#]*)";
  var regex = new RegExp(regexS);
  var results = regex.exec(window.location.search);
  if(results == null)
    return undefined;
  else
    return decodeURIComponent(results[1].replace(/\+/g, " "));
};


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

  var CurrentStoryList = Backbone.Collection.extend({
    model: Story,
    url: "/api/current/",
    parse: function (json) {
      return json.objects;
    },
    getStoryByType: function (type) {
      return this.where({story_type: type});
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

        if (i % modelLength === 0 && i > 0)
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

      }, STORY_ANIMATION_DELAY);

      window.wafwfyApp.trigger('widgetRendered');
      return this;
    }
  });

  var EpicsWidget = Backbone.View.extend({
    initialize: function () {
      this.render();
    },
    render: function () {
      var chart = new Highcharts.Chart({
        chart: {
          renderTo: 'tags-chart',
          type: 'bar',
          margin: [ 0, 0, 0, 150],
          backgroundColor: 'transparent',
          borderColor: 'transparent'
        },
        colors: [
          '#44a3aa',
          '#e3a21a',
          '#99b433'
        ],
        title: {
          text: null
        },
        xAxis: {
          categories: window.epics,
          gridLineColor: 'transparent',
          labels: {
            style: {
              color: '#FFFFFF',
              'font-weight': 'bold'
            }
          }
        },
        yAxis: {
          min: 0,
          gridLineColor: 'transparent'
        },
        legend: {
          enabled: false
        },
        tooltip: {
          enabled: false
        },
        plotOptions: {
          series: {
            stacking: 'normal'
          },
          bar: {
            dataLabels: {
              style: {
                color: '#FFFFFF',
                'font-weight': 'bold'
              }
            }
          }
        },
        credits: {
          enabled: false
        },
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
        'accepted': 2
      };

      $.get('/api/epics/').done(function (data) {
        var points;
        $.each(data.objects, function (epic) {
          points = [0, 0, 0];
          $.each(data.objects[epic], function (state) {
            var series = state_to_series[state];
            if (series === undefined)
              series = 1;
            points[series] += data.objects[epic][state];
          });
          $(points).each(function (i, el) {
            chart.series[i].addPoint([epic, el]);
          });
        });
      });

      window.wafwfyApp.trigger('widgetRendered');
      return this;
    }
  });

  var VelocityChartWidget = Backbone.View.extend({
    initialize: function () {
      this.render();
    },
    render: function () {
      $.get('/api/velocity/last/10/').done(function (data) {
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

      window.wafwfyApp.trigger('widgetRendered');
      return this;
    }
  });

  var MetroUIWafwfyApp = Backbone.View.extend({
    el: $(".gridster ul"),
    arrayPositionLeft: [],
    leftBase: 0,
    widgets: [
      CurrentStoryListView,
      EpicsWidget,
      VelocityChartWidget
    ],
    initialize: function () {
      this.on('widgetRendered', this.updateWidgetOffSet, this);

      // is wafwfy animated?
      if (getParameterByName("animated") !== undefined)
        this.move();
      else
        $('.metro-scroll').mousewheel(function (event, delta) {
          this.scrollLeft -= (delta * 30);
        });

      return this;
    },
    updateWidgetOffSet: function () {
      var self = this;
      self.arrayPositionLeft = [];

      $('.metro-section').each(function () {
        self.leftBase = $('.metro-sections').offset().left;
        self.arrayPositionLeft.push($(this).offset().left - self.leftBase);
      });
    },
    move: function () {
      var currentPosition = 0
        , self = this;

      setInterval(function () {
        currentPosition++;
        if (currentPosition > self.arrayPositionLeft.length - 2)
          currentPosition = 0;

        $('.metro-sections').animate({'left': -self.arrayPositionLeft[currentPosition]}, ANIMATION_SPEED)
      }, ANIMATION_DELAY);
    },
    render: function () {
      _.each(this.widgets, function (Widget) {
        new Widget();
      }, this);

      setTimeout(
        function () {
          document.location.reload(true);
        },
        30*60*1000
      );

      return this;
    }
  });

  window.wafwfyApp = new MetroUIWafwfyApp();
  window.wafwfyApp.render();
});
