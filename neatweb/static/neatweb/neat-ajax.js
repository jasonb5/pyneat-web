$(document).ready(function() {
  $('#experiments').change(function() {
    var expId;

    expId = $(this).val()

    $.get('/neat/experiment/', {experiment_id: expId}, function(data) {
      $('#test').html(data)
    });
  });
});
