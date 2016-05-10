$(document).ready(function () {
  $.fn.extend({
    updateAction: function (selectedId, prePath) {
      var selected = $(selectedId).val();
      $(this).attr('action', prePath.concat(selected, '/'));
    },
  });

  function update_status () {
    $.get('/neat/progress', function (data) {
      var json = $.parseJSON(data);

      json.forEach(function (v, i) {
        var endCol = $('#'+v.jid);
        var progress = parseInt(v.progress);

        if (progress > 0 && progress < 100) {
          if ($('#progress-'+v.jid).length) {
            Ink.requireModules(['Ink.UI.ProgressBar_1'], function (ProgressBar) {
              var progressBar = new ProgressBar('#progress-'+v.jid);
              progressBar.setValue(progress);
            });
          } else{
            endCol.attr('data-progress', 'progress');
            endCol.html("<div id=\"progress-"+v.jid+"\" \
                class=\"ink-progress-bar grey\" \
                data-start-value=\""+progress+"\"><span class=\"caption\"> \
                Progress</span><div class=\"bar grey\"></div></div>");
          }
        } else if (progress == 200) {
          if (endCol.attr('data-progress') != 'undefined') {
            endCol.removeAttr('data-progress');
            endCol.html(v.end);
          }
        }
      });
    }); 
  }

  if ($(location).attr('pathname') === '/neat/') {
    update_status();
    setInterval(update_status, 1000);
  } else {
    clearInterval(update_status);
  }

  function update_graph(id, type) {
    $.get('/neat/graphs', { id: id, type: type }, function(data) {
      var xdata = [];
      var ydata = [];

      var json = $.parseJSON(data);

      for (var i = 0; i < json.data.length; ++i) {
        xdata.push(json.data[i].xdata);
        ydata.push(json.data[i].ydata);
      }

      var gdata = [
        {
          x: xdata,
          y: ydata,
          type: json.type,
        }
      ];

      var layout = {
        title: json.title,
        xaxis: {
          title: json.xtitle,
        },
        yaxis: {
          title: json.ytitle,
        },
      };

      Plotly.newPlot('graph', gdata, layout);
    });
  }

  $('#graph-selection').ready(function() {
    var id = $('li.active a').attr('href').match(/\/([0-9]+)\/$/i)[1];
    var type = $('#graph-selection option:selected').val();

    update_graph(id, type);
  });

  $('#graph-selection').change(function() {
    var id = $('li.active a').attr('href').match(/\/([0-9]+)\/$/i)[1];
    var type = $('#graph-selection option:selected').val();

    update_graph(id, type);
  });

  $('#test-data').click(function () {
    var data = [];

    $('#data').children().each(function (i) {
      var test = [];

      $(this).children('#output').each(function (j) {
        var id = $(this).attr('data-id');
        test[id] = $(this).val();
      });

      data.push(test);
    });

    $.get('/neat/simulate/fitness', 
        { func: $('#id_fitness_func').val(), data: JSON.stringify(data) }, 
        function (data) {
          var json = $.parseJSON(data);
          $('#fitness').html(json.fitness);
          $('#winner').html(Boolean(json.winner));
        }
    );
  });

  $('#add-data').click(function () {
    var num_output = $('#id_num_output').val();
    var data_div = $('#data');

    var test_div = $('<div>', { id: 'test' });

    test_div.append($('<strong>', { text: 'Output' }));
    test_div.append($('<br>'));

    for (i = 0; i < num_output; ++i) {
      test_div.append($('<input>', { id: 'output', 'data-id': i, type: 'number', value: 0 }));
    }

    test_div.append($('<a>', 
          { 
            'data-id': i, 
            text: 'x', 
            class: 'left-space', 
            type: 'button', 
            click: function () {
              $(this).parent().remove();
            },
          }));
    test_div.append($('<hr>', { class: 'right-space' }));

    data_div.prepend(test_div); 
  });

  $('#population-form').ready(function () {
    $('#population-form').updateAction('#population-sel option:selected', '/neat/population/');
  });

  $('#population-sel').change(function () {
    $('#population-form').updateAction('#population-sel option:selected', '/neat/population/');
  });

  $('#generation-form').ready(function () {
    $('#generation-form').updateAction('#generation-sel option:selected', '/neat/generation/');
  });

  $('#generation-sel').change(function () {
    $('#generation-form').updateAction('#generation-sel option:selected', '/neat/generation/');
  });

  $('#species-form').ready(function () {
    $('#species-form').updateAction('#species-sel option:selected', '/neat/species/');
  });

  $('#species-sel').change(function () {
    $('#species-form').updateAction('#species-sel option:selected', '/neat/species/');
  });

  $('#organism-form').ready(function () {
    $('#organism-form').updateAction('#organism-sel option:selected', '/neat/organism/');
  });

  $('#organism-sel').change(function () {
    $('#organism-form').updateAction('#organism-sel option:selected', '/neat/organism/');
  });
});
