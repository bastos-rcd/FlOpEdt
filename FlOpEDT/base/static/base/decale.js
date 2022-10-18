// This file is part of the FlOpEDT/FlOpScheduler project.
// Copyright (c) 2017
// Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
// Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public
// License along with this program. If not, see
// <http://www.gnu.org/licenses/>.
// 
// You can be released from the requirements of the license by purchasing
// a commercial license. Buying such a license is mandatory as soon as
// you develop activities involving the FlOpEDT/FlOpScheduler software
// without disclosing the source code of your own applications.

var select_orig_date;
var select_prof = d3.select("[id=prof]");
var select_gp = d3.select("[id=gp]");
//var select_sem =  d3.select("[id=init_se]");

var default_dd = " * ";

var filtered = {
  week: week_init,
  year: year_init,
  mod_prof_gp: [
    { title: gettext('Module    '), id: 'fil-mod', get: 'm', arr: [default_dd], val: default_dd },
    { title: gettext("Teacher    "), id: 'fil-prof', get: 'p', arr: [default_dd], val: default_dd },
    { title: gettext('Group    '), id: 'fil-gp', get: 'g', arr: [default_dd], val: default_dd }],
  //[,[default_dd],[default_dd]],
  chosen: [0, 0, 0]
};

var aim = { week: 0, year: 0, prof: '' };

var liste_cours = [];

var liste_aim_prof = [];

var first_when = true;

var commit = [];


initiate();


function min_to_hm_txt(minutes) {
  var h = Math.floor(minutes / 60);
  var m = minutes - h * 60;
  var mt = '';
  if (m != 0) {
    mt = m.toString().padStart(2, '0');
  }
  return h + "h" + mt;
}


function initiate() {

  var i = 0;
  let found = false;


  // current user as first choice
  while (!found && i < profs.length) {
    if (profs[i] != usna) {
      found = true;
    } else {
      i += 1;
    }
  }
  if (i < profs.length && profs.length > 0) {
    var tmp = profs[0];
    profs[0] = profs[i];
    profs[i] = tmp;
  }
  fill_aim_prof([]);


  // create drop down for week selection
  select_orig_date = d3.select("[id=orig_date]");
  select_orig_date.on("change", function () { choose_week(true); });
  select_orig_date
    .selectAll("option")
    .data(week_year_list)
    .enter()
    .append("option")
    .text(function (d) { return d['year']+'-'+d['week']; });


  // data selection
  aim.prof = usna;
  aim.week = week_year_list[0].week;
  aim.year = week_year_list[0].year;


  // called with get parameters
  if (filtered.week != -1 || filtered.year != -1) {

    update_after_first();

    d3
      .select(".scheduled")
      .attr("checked", "checked");

    select_orig_date
      .selectAll("option")
      .each(function (d, i) {
        if (d.week == week_init && d.year == year_init) {
          d3.select(this).attr("selected", "");
        }
      });
  }

  create_dd();
  go_dd();

}


// fetch the data corresponding to the current selection
function go_filter() {
  var sel, di, sa, i, cur;
  var url_fd_full = url_fetch_decale + "?a=" + filtered.year + "&s=" + filtered.week;
  var prof_changed = false;

  // remember the current selections (module, prof, group)
  for (i = 0; i < 3; i++) {
    sel = d3.select("[id=" + filtered.mod_prof_gp[i].id + "]");
    di = sel.property('selectedIndex');
    sa = sel
      .selectAll("option")
      .filter(function (d, i) { return i == di; })
      .datum();
    if (sa != default_dd) {
      if (typeof sa === "string") {
        url_fd_full += "&" + filtered.mod_prof_gp[i].get + "=" + sa;
      } else {
        let keys = Object.keys(sa) ;
        for( let i = 0 ; i < keys.length ; i++) {
          url_fd_full += "&" + keys[i]
            + "=" + sa[keys[i]];
        }
      }
    }
    if (i == 1 && sa != filtered.mod_prof_gp[i].val) {
      prof_changed = true;
    }
    filtered.mod_prof_gp[i].val = sa;
  }

  // remember current targeted prof
  sel = d3.select("[id=aim_prof]");
  di = sel.property('selectedIndex');
  sa = sel
    .selectAll("option")
    .filter(function (d, i) { return i == di; })
    .datum();
  if (prof_changed) {
    if (filtered.mod_prof_gp[1].val == default_dd) {
      sa = usna;
    } else {
      sa = filtered.mod_prof_gp[1].val;
    }
    aim.prof = sa;
  }

  show_loader(true);
  $.ajax({
    type: "GET",
    dataType: 'json',
    url: url_fd_full,
    async: false,
    contentType: "application/json; charset=utf-8",
    success: function (msg) {
      // console.log(msg);
      // console.log("success");
      // console.log(msg.modules);
      filtered.mod_prof_gp[0].arr = msg.modules;
      filtered.mod_prof_gp[1].arr = msg.profs;
      filtered.mod_prof_gp[2].arr = msg.groups;
      liste_cours = msg.cours;
      liste_jours = {};
      for (i = 0; i < msg.jours.length; i++) {
        cur = msg.jours[i];
        liste_jours[cur.ref] = { date: cur.date, name: cur.name };
      }

      fill_aim_prof(msg.profs_module);


      for (i = 0; i < 3; i++) {
        // console.log(i);
        // console.log(filtered.mod_prof_gp[i].arr);
        filtered.mod_prof_gp[i].arr.unshift(default_dd);
      }

      go_dd();
      go_dd_aim();

      // rebuild the previously selected elements
      for (i = 0; i < 3; i++) {
        let found = false;
        let j = 0;
        while (!found && j < filtered.mod_prof_gp[i].arr.length) {
          if (filtered.mod_prof_gp[i].arr[j] == filtered.mod_prof_gp[i].val) {
            found = true;
          } else {
            j += 1;
          }
        }
        if (!found) {
          document.getElementById(filtered.mod_prof_gp[i].id).selectedIndex = 0;
        } else {
          document.getElementById(filtered.mod_prof_gp[i].id).selectedIndex = j;
        }
      }

      // rebuild the previously targeted prof
      let found = false;
      let j = 0;
      while (!found && j < liste_aim_prof.length) {
        if (liste_aim_prof[j] == sa) {
          found = true;
        } else {
          j += 1;
        }
      }
      document.getElementById("aim_prof").selectedIndex = j;


      go_cours();
      show_loader(false);

    },
    error: function (msg) {
      console.log("error");
      show_loader(false);
    },
    complete: function (msg) {
      // console.log("complete");
      show_loader(false);
    }
  });
}

// fill drop down list of targeted prof
function fill_aim_prof(pm) {
  var i;
  liste_aim_prof = [];
  liste_aim_prof.push(usna);
  liste_aim_prof.push("");

  for (i = 0; i < pm.length; i++) {
    if (pm[i] != usna) {
      liste_aim_prof.push(pm[i]);
    }
  }
  if (pm.length > 0) {
    liste_aim_prof.push("");
  }
  for (i = 0; i < profs.length; i++) {
    if (!liste_aim_prof.includes(profs[i])) {
      liste_aim_prof.push(profs[i]);
    }
  }
}


// route action when validate
function is_orph() {
  if (first_when) {
    update_after_first();
  }

  if (document.getElementById("canceled").checked) {
    filtered.week = 0;
    filtered.year = 0;
    go_filter();
  } else if (document.getElementById("pending").checked) {
    filtered.week = 1;
    filtered.year = 0;
    go_filter();
  } else {
    choose_week(false);
  }
}

// create drop down lists for targeted mod-prof-gp and actions
function create_dd() {
  d3.select(".div-filt")
    .selectAll("select")
    .data(filtered.mod_prof_gp)
    .enter()
    .append("span")
    .attr("class", "crit")
    .text(function (d) { return d.title; })
    .append("select")
    .attr("id", function (d) { return d.id; })
    .on("change", go_filter);

  var di = d3.select(".div-aim")
    .append("div");

  di
    .append("input")
    .attr("type", "radio")
    .attr("name", "aim")
    .attr("id", "cancel");

  di.append("label")
    .attr("for", "cancel")
    .text(gettext("Definitely cancel"));

  di.append("br");

  di
    .append("input")
    .attr("type", "radio")
    .attr("name", "aim")
    .attr("id", "pend");

  di.append("label")
    .attr("for", "pend")
    .text(gettext("Put on hold"));



  di = d3.select(".div-aim")
    .append("div");
  di
    .append("input")
    .attr("type", "radio")
    .attr("name", "aim")
    .attr("id", "move");

  var rad = di
    .append("label");

  rad
    .append("span")
    .text(gettext("Move to week "))
    //
    //    rad
    .append("select")
    .attr("id", "aim_date")
    .on("change", function (d) { choose_aim('d'); });
  //    
  rad
    .append("span")
    .attr("class", "crit")
    .text(gettext("by "))
    .append("select")
    .attr("id", "aim_prof")
    .on("change", function (d) { choose_aim('p'); });

  d3.select("[id=aim_date]")
    .selectAll("option")
    .data(week_year_list)
    .enter()
    .append("option")
    .attr("value", function (d) { return d['week']; })
    .text(function (d) { return d['year']+'-'+d['week']; });

  go_dd_aim();

}


// update aimed dd lists
function go_dd_aim() {

  var sel = d3.select("[id=aim_prof]")
    .selectAll("option")
    .data(liste_aim_prof, function (d, i) { return i; });

  sel
    .enter()
    .append("option")
    //        .merge(sel.select("option"))
    .attr("value", function (d) { return d; })
    .text(function (d) { return d; });


  d3.select("[id=aim_prof]")
    .selectAll("option")
    .attr("value", function (d) { return d; })
    .text(function (d) { return d; });


  d3.select("[id=aim_prof]")
    .selectAll("option")
    .exit()
    .remove();


}

// action when the aimed date or the aimed prof is chosen
function choose_aim(dop) {
  document.getElementById("cancel").checked = false;
  document.getElementById("pend").checked = true;
  document.getElementById("move").checked = true;


  if (dop == 'd') {
    var select_aim_date = d3.select("[id=aim_date]");

    var di = select_aim_date.property('selectedIndex');
    var sa = select_aim_date
      .selectAll("option")
      .filter(function (d, i) { return i == di; })
      .datum();

    aim.week = sa.week;
    aim.year = sa.year;
  } else {
    var select_aim_prof = d3.select("[id=aim_prof]");

    let di = select_aim_prof.property('selectedIndex');
    let sa = select_aim_prof
      .selectAll("option")
      .filter(function (d, i) { return i == di; })
      .datum();

    aim.prof = sa;
  }
}


// update dd lists for mod-prof-gp
function go_dd() {
  var all_sel = d3.select(".div-filt")
    .selectAll("select")
    .selectAll("option");

  var res = all_sel
    .data(function (d, i, j) { return d.arr; })
    .enter()
    .append("option")
    //	.merge(all_sel)
    .attr("value", function (d) { return d; })
    .text(function (d) { return d; });

  var se = d3.select(".div-filt")
    .selectAll("select")
    .selectAll("option")
    .data(function (d, i, j) { return d.arr; })
    .attr("value", function (d) { return d; })
    .text(function (d) {
      if (typeof d === "string") {
        return d ;
      } else {
        return Object.values(d).join("-") ;
      }
    });


  se
    .exit()
    .remove();

  // d3.select(".div-filt")
  // 	.selectAll("select")
  // 	.selectAll("option")
  // 	.data(function(d,i,j){return d.arr;})
}

// make the valider button to appear after the first choice
function update_after_first() {
  first_when = false;
  d3.select(".msg-sem").text("");

  d3.select("[id=but-val]")
    .append("input")
    .attr("class", "crittop")
    .attr("type", "button")
    .attr("value", gettext("Confirm"))
    .on("click", send_cours);
}



function send_cours() {

  var cked = '';
  if (document.getElementById("move").checked) {
    cked = "move";
  } else if (document.getElementById("pend").checked) {
    cked = "pend";
  } else if (document.getElementById("cancel").checked) {
    cked = "cancel";
  }

  commit = [];


  d3.select(".cours")
    .selectAll(".ck")
    .select("input")
    .each(function (d, i) {
      if (d3.select(this).property("checked")) {
        commit.push(d);
      }
    });
  console.log(JSON.stringify(commit));

  if (commit.length == 0) {
    change_ack(gettext("No checked box, no moved course!"));
    return;
  }
  if (cked == "move" && aim.prof == "") {
    if (!(window.confirm(gettext('You want these courses to have no tutor, right?')))) {
      change_ack(gettext("Then please assign these courses to someone."));
      return;
    }
  }

  if (cked != "cancel" && cked != "move" && cked != "pend") {
    change_ack(gettext("Chose the action you want to do."));
  } else {
    var tot = {
      os: filtered.week,
      oa: filtered.year,
      ns: aim.week,
      na: aim.year,
      np: aim.prof
    };

    if (cked == "pend") {
      tot.ns = 1;
      tot.na = 0;
    }
    if (cked == "cancel") {
      tot.ns = 0;
      tot.na = 0;
    }

    var sent_data = {};
    sent_data['new'] = JSON.stringify(tot);
    sent_data['liste'] = JSON.stringify(commit);
    console.log(sent_data);

    show_loader(true);
    $.ajax({
      url: url_change_decale,
      type: 'POST',
      //	    contentType: 'application/json; charset=utf-8',
      data: sent_data, //JSON.stringify({'new':tot,'liste':commit}),
      dataType: 'json',
      success: function (msg) {
        recv(msg.responseText);
        show_loader(false);
      },
      error: function (msg) {
        recv(msg.responseText);
        show_loader(false);
      }
    });
  }
}


function recv(msg) {
  var i;

  console.log("lc", liste_cours);
  console.log("c", commit);

  d3.select(".cours")
    .selectAll(".ck")
    .select("input")
    .property('checked', false);


  if (msg == 'OK') {
    for (i = 0; i < commit.length; i++) {
      var r = liste_cours.indexOf(commit[i]);
      console.log(r);
      if (r > -1) {
        liste_cours.splice(r, 1);
      }
    }
  }

  go_cours();

  commit = [];

  change_ack(msg);
}

function change_ack(msg) {
  var old = d3.select("[id=ack]").text();
  if (msg == old) {
    msg += ".";
  }
  d3.select("[id=ack]").text(msg);
  console.log(msg);
}


function go_cours() {
  var all_cours = d3.select(".cours")
    .selectAll(".ck")
    .data(liste_cours, function (d, i) { return i; });

  var co = all_cours
    .enter()
    .append("div")
    .attr("class", "ck");

  co
    .append("input")
    .attr("type", "checkbox")
    .attr("id", function (d, i) { return "c" + i; });

  co
    .append("label")
    .attr("for", function (d, i) { return "c" + i; })
    .merge(all_cours.select("label"))
    .text(plot_cours);


  all_cours
    .exit()
    .remove();
}


function plot_cours(d) {
  var ret = d.m + "-" + d.p + "-" + d.g.join(",") + " (";
  var h, m;
  if (d.d != '') {
    ret += liste_jours[d.d].name + " " + liste_jours[d.d].date + " ";
    ret += min_to_hm_txt(d.t);
  } else {
    ret += gettext("not scheduled");
  }
  ret += ")";
  return ret;
}

function choose_week(check) {
  if (check) {
    // check radio button
    document.getElementById("canceled").checked = false;
    document.getElementById("scheduled").checked = true;
  }

  //(could not do it in d3) d3.select(".scheduled").attr("checked","true");

  // change weeks

  // change origin week
  var di = select_orig_date.property('selectedIndex');
  var sa = select_orig_date
    .selectAll("option")
    .filter(function (d, i) { return i == di; })
    .datum();

  filtered.week = sa.week;
  filtered.year = sa.year;

  // and change targeted week
  document.getElementById("aim_date").selectedIndex = select_orig_date.property('selectedIndex');
  aim.week = filtered.week;
  aim.year = filtered.year;


  // does not work properly
  // dd list selected attribute is not always refreshed...

  // d3.select("[id=aim_date]")
  // 	.selectAll("option")
  // 	.each(function(d,i) {
  // 	    if (d.week==sa.week && d.year==sa.year){
  // 		d3.select(this).attr("selected","");
  // 		console.log(d);
  // 	    }
  // 	});


  // filter again
  go_filter();
}
