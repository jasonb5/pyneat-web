$(document).ready(function() {
  $.fn.exists = function() {
    return this.length !== 0;
  }

  $('button#show').click(function() {
    var exp_id = $(this).attr('data-id');

    $.get('/neat/experiment/', { experiment_id: exp_id }, function(data) {
      var exp = $.parseJSON(data);
      
      var details = $('#details');

      if (details.exists()) {
        $.each(exp, function(k, v) {
          if (k == 'fitness_func') {
            $('#' + k).html('<textarea rows="10" cols="75">' + v + '</textarea>');
          } else {
            $('#' + k).html(v);
          }
        });
      } else {
        var tbl = '<table id="details" border="1">';

        $.each(exp, function(k, v) {
          tbl += '<tr>';
          tbl += '<td>' + k + '</td>';
          if (k === 'fitness_func') {
            tbl += '<td id="' + k + '"><textarea rows="10" cols="75">' + v + '</textarea></td>';
          } else {
            tbl += '<td id="' + k + '">' + v + '</td>';
          }
          tbl += '</tr>'; 
        });

        tbl += '</table>';

        $('body').append(tbl);
      }
    });    
  });

  $('#organisms').change(function() {
    var orgId = $(this).val();

    $.get('/neat/organism/', {organism_id: orgId}, function(data) {
      var org = jQuery.parseJSON(data);

      $('#fitness').html(org.fitness);
      $('#rank').html(org.rank);
      $('#marked').html(org.marked.toString());

      try {
        var network = jQuery.parseJSON(org.network);
        var table = '<table border="1"><tr><td>Inode</td><td>Onode</td><td>Weight</td><td>Enabled</td></td>';

        $('#input').html(network.input);
        $('#hidden').html(network.hidden);
        $('#output').html(network.output);

        $.each(network.genes, function() {
          table += '<tr>';
          table += '<td>' + this['inode'] + '</td>';
          table += '<td>' + this['onode'] + '</td>';
          table += '<td>' + this['weight'] + '</td>';
          table += '<td>' + this['enabled'] + '</td>';
          table += '</tr>';
        });

        table += '</table>';

        $('#genes').html(table);
      }
      catch (err) {
        $('#genes').html(err.message);
      }
    });
  });

  $('#species').change(function() {
    var specId = $(this).val();

    $.get('/neat/species/', {species_id: specId}, function(data) {
      var spec = jQuery.parseJSON(data);
      var updateAction = $('#spec_form').attr('action');
      var oldId = /.*\/(species-\d+)$/.exec(updateAction)[1];

      $('#spec_form').attr('action', updateAction.replace(oldId, 'species-'.concat(specId)));

      $('#organisms').html(spec.org_count)
      $('#marked').html(spec.marked.toString())
      $('#avg_fitness').html(spec.avg_fitness)
      $('#max_fitness').html(spec.max_fitness)
      $('#offspring').html(spec.offspring)
      $('#age_since_imp').html(spec.age_since_imp)
    });
  });

  $('#generations').change(function() {
    var genId = $(this).val();

    $.get('/neat/generation/', {generation_id: genId}, function(data) {
      var gen = jQuery.parseJSON(data);
      var updateAction = $('#gen_form').attr('action');
      var oldId = /.*\/(generation-\d+)$/.exec(updateAction)[1];

      $('#gen_form').attr('action', updateAction.replace(oldId, 'generation-'.concat(genId)));

      if (gen.winner) {
        $('#status').html('A winner was found!');
      } else {
        $('#status').html('A winner was not found!');
      }
    });
  });

  $('#experiments').change(function() {
    var expId = $(this).val();

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
