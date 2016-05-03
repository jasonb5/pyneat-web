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
