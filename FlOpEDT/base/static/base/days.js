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

function Day(day = {
  num: iday,
  date: "01/01",
  ref: "m",
  name: "Lun."
}) {
  this.num = day.num;
  this.date = day.date;
  this.ref = day.ref;
  this.name = day.name;
  var sp = day.date.split('/');
  this.day = +sp[0];
  this.month = +sp[1];
  this.force_here = false;
  this.init_force_here = false;
}

// maximum number of days in a month
Day.prototype.max_days_in_month = function () {
  if (this.month == 2) {
    return 29;
  } else if ([1, 3, 5, 7, 8, 10, 12].includes(this.month)) {
    return 31;
  } else {
    return 30;
  }
};



// 'static' function 
Day.id_fun = function (d) {
  return d.name + "-" + d.date;
};



function WeekDays(days) {
  this.day_list = [];
  // indexed by ref
  this.day_dict = {};
  if (typeof days !== 'undefined') {
    this.add_all(days);
  }
}

WeekDays.prototype.nb_days = function () {
  return this.day_list.length;
};

WeekDays.prototype.day_by_ref = function (ref) {
  return this.day_dict[ref];
};

WeekDays.prototype.day_by_num = function (num) {
  return this.day_list.find(function (d) {
    return d.num == num;
  });
};

WeekDays.prototype.last_day = function () {
  return this.day_by_num(
    this.day_list.reduce(
      function(a, b) {
        return {num: Math.max(a.num, b.num)} ;
      }
    ).num
  );
};

WeekDays.prototype.data = function () {
  return this.day_list;
};

WeekDays.prototype.refs = function () {
  return Object.keys(this.day_list);
};

WeekDays.prototype.forEach = function (callback, this_arg) {
  return this.day_list.forEach(callback, this_arg);
};

WeekDays.prototype.add_day = function (day = {
  num: iday,
  date: "01/01",
  ref: "m",
  name: "Lun."
}) {
  var new_day = new Day(day);
  this.day_list.push(new_day);
  this.day_dict[new_day.ref] = new_day;
};

WeekDays.prototype.add_all = function (days) {
  days.forEach(function (day) {
    this.add_day(day);
  }, this);
};

WeekDays.prototype.get_days_between = function(first_ref, last_ref) {
  let first_num = this.day_by_ref(first_ref).num ;
  let last_num = this.day_by_ref(last_ref).num ;
  if (first_num > last_num) {
    let tmp = first_num ;
    first_num = last_num ;
    last_num = tmp ;
  }
  return this.day_list.filter(function (day) {
    return day.num >= first_num && day.num <= last_num ;
  });
};

WeekDays.prototype.get_changes_physical_presence = function() {
  let changes = [] ;
  this.forEach(function(d) {
    if (d.init_force_here != d.force_here) {
      changes.push({'day':d.ref, 'force_here':d.force_here});
    }
  });
  return changes ;
};


// Name and date of the days above the grid
function WeekDayHeader(
  svg, layout_name, days, half_day_rect, par, fetch_physical_presence_base_url,
  change_physical_presence
) {
  this.layout = svg.get_dom(layout_name);
  this.mix = new WeekDayMix(par, days, this);
  this.half_day_rect = half_day_rect;
  this.url_fetch_physical_presence = fetch_physical_presence_base_url ;
  this.url_change_physical_presence = change_physical_presence ;
  hard_bind(this.mix);
}

WeekDayHeader.prototype.data = function () {
  return this.mix.days.data();
};

WeekDayHeader.prototype.update = function (quick) {
  var t = get_transition(quick);

  var day_scale = this.layout
    .selectAll(".gridsckd")
    .data(this.data(),
      Day.id_fun);

  var day_sc_g = day_scale
    .enter()
    .append("g")
    .attr("class", "gridsckd");
  

  day_sc_g
    .append("text")
    .attr("class", "txt_scl")
    .on('click', this.mix.gsckd_click)
    .merge(day_scale.select(".txt_scl"))
    .transition(t)
    .text(this.mix.gsckd_txt)
    .attr("fill", this.mix.gsckd_txt_color)
    .attr("x", this.mix.gsckd_x)
    .attr("y", this.mix.gsckd_y);

  if (this.half_day_rect) {
    day_sc_g
      .append("rect")
      .attr("class", "day_am")
      .merge(day_scale.select(".day_am"))
      .transition(t)
      .attr("x", this.mix.grid_day_am_x)
      .attr("y", this.mix.grid_day_am_y)
      .attr("height", this.mix.grid_day_am_height)
      .attr("width", this.mix.grid_day_am_width);

    day_sc_g
      .append("rect")
      .attr("class", "day_pm")
      .merge(day_scale.select(".day_pm"))
      .transition(t)
      .attr("x", this.mix.grid_day_pm_x)
      .attr("y", this.mix.grid_day_pm_y)
      .attr("height", this.mix.grid_day_pm_height)
      .attr("width", this.mix.grid_day_pm_width);
  }

  day_scale.exit().remove();
};

WeekDayHeader.prototype.fetch_physical_presence = function() {
  var exp_week = wdw_weeks.get_selected();
  // let mix = this.mix ;
  // let url = ;
  // let me = this ;

  show_loader(true);
  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    url: this.url_fetch_physical_presence + exp_week.url(),
    async: true,
    contentType: "text/csv",
    context: this,
    success: function (msg) {
      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {
        d3.csvParse(msg,  function(pres) {
          if (pres.user == user.name) {
            days_header.mix.days.day_by_ref(pres.day).force_here = true ;
            days_header.mix.days.day_by_ref(pres.day).init_force_here = true ;
          }
        });
      }
      this.update(true) ;
      show_loader(false);
    },
    error: function (xhr, error) {
      console.log("error");
      console.log(xhr);
      console.log(error);
      console.log(xhr.responseText);
      show_loader(false);
    }
  });

};

WeekDayHeader.prototype.send_change_physical_presence = function () {
  let cur_week = wdw_weeks.get_selected();
  let sent_data = {};
  sent_data['changes'] = JSON.stringify(
    this.mix.days.get_changes_physical_presence()
  );
  console.log(sent_data['changes']);
  console.log(this.mix.days.get_changes_physical_presence());

  show_loader(true);
  $.ajax({
    url: this.url_change_physical_presence + cur_week.url() + user.name  + "/",
    type: 'POST',
    data: sent_data,
    dataType: 'json',
    success: function (msg) {
      console.log(msg);
      ack.list.push({
        'status': 'OK',
        'more': ""
      }) ;
      ack.ongoing = ack.ongoing.filter(function(o){
        return o != 'presence' ;
      });
      go_ack_msg();
      show_loader(false);
    },
    error: function (msg) {
      aaaa = msg;
      ack.list.push({
        'status': 'KO',
        'more': ""
      }) ;
      ack.ongoing = ack.ongoing.filter(function(o){
        return o != 'presence' ;
      });
      go_ack_msg();
      show_loader(false);
    }
  });
} ;



// Private class
// Display parameters and functions
function WeekDayMix(par, days, header) {
  Object.assign(this, par);
  this.days = days;
  this.header = header ;

  // put it here, even if it's not useful for now
  this.gsckd_x = function (d, i) {
    return i * (rootgp_width * labgp.width +
      dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
      rootgp_width * labgp.width * .5;
  };
  this.gsckd_y = function () {
    return -.75 * labgp.height_init;
  };
  this.gsckd_txt = function (d) {
    return d.name + " " + d.date;
  };
  this.gsckd_txt_color = function(d) {
    return d.force_here?'green':'darkslateblue';
  };
  this.gsckd_click = function(d) {
    if (ckbox['dis-mod'].cked) {
      d.force_here = !d.force_here ;
      this.header.update(true);
    }
  } ;
  this.grid_day_am_x = function (d) {
    return d.num * (rootgp_width * labgp.width +
      dim_dispo.plot * (dim_dispo.width + dim_dispo.right));
  };
  this.grid_day_am_y = function () {
    return 0;
  };
  this.grid_day_am_height = function () {
    var t = department_settings.time;
    return scale * nbRows * (t.lunch_break_start_time - t.day_start_time);
  };
  this.grid_day_am_width = function () {
    return rootgp_width * labgp.width;
  };
  this.grid_day_pm_x = function (d) {
    return this.grid_day_am_x(d);
  };
  this.grid_day_pm_y = function () {
    var t = department_settings.time;
    return this.grid_day_am_y() + this.grid_day_am_height()
      + bknews_h();
  };
  this.grid_day_pm_height = function () {
    var t = department_settings.time;
    return scale * nbRows * (t.day_finish_time - t.lunch_break_finish_time);
  };
  this.grid_day_pm_width = function () {
    return rootgp_width * labgp.width;
  };

}
