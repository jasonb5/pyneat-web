$(document).ready(function () {
  $.fn.extend({
    updateAction: function (selectedId, prePath) {
      var selected = $(selectedId).val();
      $(this).attr('action', prePath.concat(selected, '/'));
    },
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
