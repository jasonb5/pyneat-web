$(document).ready(function() {
  $('#generations').change(function() {
    var genId;

    genId = $(this).children(":selected").attr("id");

    $.get('/neat/generation/', {generation_id: genId}, function(data) {
      var updateAction = $('#gen_form').attr('action');
      var oldId = /.*\/(generation-\d+)$/.exec(updateAction)[1];

      $('#gen_form').attr('action', updateAction.replace(oldId, 'generation-'.concat(genId)));
    });
  });

  $('#experiments').change(function() {
    var expId;

    expId = $(this).children(':selected').attr('id');

    $.get('/neat/experiment/', {experiment_id: expId}, function(data) {
      var conf;

      conf = jQuery.parseJSON(data);

      $('#exp_form').attr('action', '/neat/experiment-'.concat(expId))

      $('#name').val(conf.name);
      $('#runs').val(conf.runs);
      $('#pop_size').val(conf.pop_size);
      $('#generations').val(conf.generations);
      $('#input').val(conf.num_input);
      $('#output').val(conf.num_output);
      $('#mut_power').val(conf.mutate_power);
      $('#coef_matching').val(conf.coef_matching);
      $('#coef_disjoint').val(conf.ceof_disjoint);
      $('#compat_threshold').val(conf.compat_threshold);
      $('#mut_neuron').val(conf.mutate_neuron_prob);
      $('#mut_gene').val(conf.mutate_gene_prob);
      $('#mut_only').val(conf.mutate_only_prob);
      $('#mate_only').val(conf.mate_only_prob);
      $('#survival').val(conf.survival_rate);
      $('#stagnation').val(conf.stagnation_threshold);
      $('#data').html(conf.data);
      $('#fitness').html(conf.fitness_func);

      $('#test').html(data)
    });
  });
});
