// update acks
function update_acks() {
  for (key in ack_side_panel) {
    $(ack_side_panel[key].id).text(ack_side_panel[key].txt);
  }
}

// empty the ack sections of the side panel
function empty_acks() {
  for (key in ack_side_panel) {
    ack_side_panel[key].txt = '';
  }
  update_acks();
}


// receive results and display in ack sections
function format_acks(msg, key_ack) {
  if (msg.status == 'OK') {
    ack_side_panel[key_ack].txt = 'OK. ' + msg.more;
  } else {
    ack_side_panel[key_ack].txt = 'KO! ' + msg.more;
  }
  update_acks();
}



// open side panel
function openNav() {

  is_side_panel_open = true;

  // open panel
  $("#side_panel").show();
  document.getElementById("side_panel").style.width = "250px";
  document.getElementById("edt-main").style.marginLeft = "250px";
  document.getElementById("menu-edt").style.marginLeft = "250px";

  // add event listener
  $('#dd_work_copy').on('change', function (e) {
    num_copie = +this.value;
    fetch_status.course_saved = false;
    fetch_all(false, false);
  });

  // fetch the copy numbers
  fetch_work_copy_numbers(false);
}

// Fetch the available work copy numbers for the current week
function fetch_work_copy_numbers(fetch_all_callback, fetch_all_callback_arg) {
  var cur_week = wdw_weeks.get_selected();

  $.ajax({
    type: "GET",
    dataType: 'json',
    url: url_work_copies + cur_week.url(),
    async: true,
    contentType: "application/json; charset=utf-8",
    success: function (msg) {
      update_work_copy_numbers(msg.copies);
      if (fetch_all_callback) {
        fetch_all(fetch_all_callback_arg, false);
      }
    },
    error: function (msg) {
      console.log("error");
    }
  });

}

// refresh the work copy dropdown list
function update_work_copy_numbers(copies) {
  // remove old copy numbers
  var dd = document.getElementById("dd_work_copy");
  while (dd.firstChild) {
    dd.removeChild(dd.firstChild);
  }

  // add new copy numbers
  var option;
  for (var i = 0; i < copies.length; i++) {
    option = { value: copies[i], text: copies[i] };
    $('#dd_work_copy').append($('<option>', option));
  }

  if (copies.length == 0) {
      num_copie = 0 ;
  } else {
    let inum_copie = copies.indexOf(num_copie) ;
    if (inum_copie == -1) {
      inum_copie ++ ;
    }
    num_copie = copies[inum_copie] ;
    $('#dd_work_copy').val(num_copie) ;
  }
  
}

// close the side panel
function closeNav() {
  // avoid fetching work copy numbers if closed
  is_side_panel_open = false;

  // close panel
  $("#side_panel").hide();
  document.getElementById("side_panel").style.width = "0";
  document.getElementById("edt-main").style.marginLeft = "0";
  document.getElementById("menu-edt").style.marginLeft = "0";

}


// swap the current work copy with the public work copy, i.e. #0
// display the old public copy afterwards
function swap_with_copy_0() {
  var cur_week = wdw_weeks.get_selected();

  show_loader(true);
  $.ajax({
    type: "GET",
    dataType: 'json',
    url: url_swap + cur_week.url() + '/' + num_copie,
    async: true,
    contentType: "application/json; charset=utf-8",
    success: function (msg) {
      format_acks(msg, 'swap');
      if (msg.status == 'OK') {
        num_copie = 0;
        $('#dd_work_copy option[value="0"]').prop('selected', true);
      }
      fetch_all(false, false);
      show_loader(false);
    },
    error: function (msg) {
      ack_side_panel['swap'].txt = 'Problème côté serveur';
      update_acks();
      show_loader(false);
    }
  });
}


// check chether the swap is feasible
function check_swap_with_copy_0() {
  var cur_week = wdw_weeks.get_selected();

  show_loader(true);
  $.ajax({
    type: "GET",
    dataType: 'json',
    url: url_check_swap + cur_week.url() + '/' + num_copie,
    async: true,
    contentType: "application/json; charset=utf-8",
    success: function (msg) {
      format_acks(msg, 'check-swap');
      show_loader(false);
    },
    error: function (msg) {
      ack_side_panel['check-swap'].txt = 'Problème côté serveur';
      update_acks();
      show_loader(false);
    }
  });
}

// delete work_copy and reload
function delete_work_copy() {
  var cur_week = wdw_weeks.get_selected();
  let ok = true;

  if (num_copie==0){
    ok = confirm("Êtes-vous sûr de vouloir supprimer la copie visible?")
  }

  if (ok){
    show_loader(true);
    $.ajax({
      type: "GET",
      dataType: 'json',
      url: url_delete_work_copy + cur_week.url() + '/' + num_copie,
      async: true,
      success: function (msg) {
        format_acks(msg, 'delete');
        fetch_all(false, true);
        show_loader(false);
      },
      error: function (msg) {
        ack_side_panel['delete'].txt = 'Problème côté serveur';
        console.log("error");
        show_loader(false);
      }
    });
  }
}

// duplicate work_copy and reload
function duplicate_work_copy() {
  var cur_week = wdw_weeks.get_selected();
  let ok = true;

  if (ok){
    show_loader(true);
    $.ajax({
      type: "GET",
      dataType: 'json',
      url: url_duplicate_work_copy + cur_week.url() + '/' + num_copie,
      async: true,
      success: function (msg) {
        format_acks(msg, 'duplicate');
        fetch_all(false, true);
        show_loader(false);
      },
      error: function (msg) {
        ack_side_panel['duplicate'].txt = 'Problème côté serveur';
        console.log("error");
        show_loader(false);
      }
    });
  }
}

// delete all unused work_copies and reload
function delete_all_unused_work_copies() {
  var cur_week = wdw_weeks.get_selected();
  let ok = true;
  ok = confirm("Êtes-vous sûr de vouloir supprimer toutes les copies sauf la 0?");

  if (ok){
    show_loader(true);
    $.ajax({
      type: "GET",
      dataType: 'json',
      url: url_delete_all_unused_work_copies + cur_week.url(),
      async: true,
      success: function (msg) {
        format_acks(msg, 'delete_all_unused');
        fetch_all(false, true);
        show_loader(false);
      },
      error: function (msg) {
        ack_side_panel['delete_all_unused'].txt = 'Problème côté serveur';
        console.log("error");
        show_loader(false);
      }
    });
  }
}


// reassign rooms and reload
function reassign_rooms() {
  var cur_week = wdw_weeks.get_selected();

  show_loader(true);
  $.ajax({
    type: "GET",
    dataType: 'json',
    url: url_reassign_rooms + cur_week.url() + '/' + num_copie,
    async: true,
    contentType: "application/json; charset=utf-8",
    success: function (msg) {
      console.log(msg);
      format_acks(msg, 'reassign_rooms');
      fetch_all(false, true);
      show_loader(false);
    },
    error: function (msg) {
      ack_side_panel['reassign_rooms'].txt = 'Problème côté serveur';
      console.log("error");
      show_loader(false);
    }
  });
}

// reassign rooms and reload
function duplicate_in_other_weeks() {
  var cur_week = wdw_weeks.get_selected();

  show_loader(true);
  $.ajax({
    type: "GET",
    dataType: 'json',
    url: url_duplicate_in_other_weeks + cur_week.url() + '/' + num_copie,
    async: true,
    contentType: "application/json; charset=utf-8",
    success: function (msg) {
      console.log(msg);
      format_acks(msg, 'duplicate_in_other_weeks');
      fetch_all(false, true);
      show_loader(false);
    },
    error: function (msg) {
      ack_side_panel['duplicate_in_other_weeks'].txt = 'Problème côté serveur';
      console.log("error");
      show_loader(false);
    }
  });
}



var ack_side_panel = {
  'swap': { id: 'swap' },
  'check-swap': { id: 'check-swap' },
  'delete':{id:'delete'},
  'delete_all_unused':{id: 'delete_all_unused'},
  'duplicate': {id: 'duplicate'},
  'reassign_rooms': {id: 'reassign_rooms'},
  'duplicate_in_other_weeks': {id: 'duplicate_in_other_weeks'}
};
for (key in ack_side_panel) {
  ack_side_panel[key].id = '#ack-' + ack_side_panel[key].id;
}
empty_acks();
