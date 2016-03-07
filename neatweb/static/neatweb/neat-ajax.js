$(document).ready(function() {
  $('#experiments').change(function() {
    var expId;

    expId = $(this).val()

    $.get('/neat/experiment/', {experiment_id: expId}, function(data) {
      var conf;

      conf = jQuery.parseJSON(data);

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
