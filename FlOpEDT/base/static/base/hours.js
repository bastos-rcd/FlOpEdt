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


function Hours(settings) {
  // side time scale: list of {min: int, hd:('am'|'pm')}
  this.data = [];
  this.settings = settings ;

  this.add_time = function(t) {
    t = +t ;
    let to_push = { min: t, hd: 'am' } ;
    if (t > this.settings.lunch_break_start_time) {
      if (t < this.settings.lunch_break_finish_time) {
        return ;
      }
      to_push.hd = 'pm' ;
    }
    let already = this.data.filter(function(t) {
      return (t.hd == to_push.hd
              && to_push.min - t.min < 10
              && t.min - to_push.min < 10);
    });
    if (already.length == 0) {
      this.data.push(to_push);
      if (t == this.settings.lunch_break_start_time
          && t == this.settings.lunch_break_finish_time) {
        this.data.push({min:t, hd: 'pm'}) ;
      }
    }
  } ;

  this.clear = function() {
    this.data = [] ;
  } ;

  this.add_times = function(time_list) {
    for (let i = 0 ; i < time_list.length ; i++) {
      this.add_time(time_list[i]);
    }
  } ;
  
  var stime = Math.ceil(settings.day_start_time / 60);
  while (stime * 60 <= settings.day_finish_time) {
    this.add_time(stime * 60) ;
    stime++;
  }
  
  if (settings.lunch_break_finish_time !=
      settings.lunch_break_start_time) {
    this.add_time(settings.lunch_break_start_time) ;
    this.add_time(settings.lunch_break_finish_time) ;
  }

  if (settings.day_start_time % 60 != 0) {
    this.add_time(settings.day_start_time);
  }
  if (settings.day_finish_time % 60 != 0) {
    this.add_time(settings.day_finish_time);
  }
  
}


// Hour labels to the left of the grid
function HourHeader(svg, layout_name, hours) {
  this.layout = svg.get_dom(layout_name).append("g").attr("class", "hour-scale");
  this.hours = hours;
  this.mix = new HourMix(this.hours.settings);
  // free_text: list of {texts: list of string, time: {min: int, hd }}
  this.free_text = [] ;
  hard_bind(this.mix);
}

HourHeader.prototype.update = function (quick) {

  var t = get_transition(quick);

  var hour_bar = this.layout
    .selectAll(".gridsckhb")
    .data([department_settings.time]);

  var hourbar_g = hour_bar
    .enter()
    .append("g")
    .attr("class", "gridsckhb");

  hourbar_g
    .append("line")
    .attr("class", "gridsckhlam")
    .merge(hour_bar.select(".gridsckhlam"))
    .transition(t)
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", 0)
    .attr("y2", bknews_top_y());

  hourbar_g
    .append("line")
    .attr("class", "gridsckhlpm")
    .merge(hour_bar.select(".gridsckhlpm"))
    .transition(t)
    .attr("x1", 0)
    .attr("y1", bknews_bot_y())
    .attr("x2", 0)
    .attr("y2", grid_height());

  hour_bar.exit().remove();

  var hour_scale = this.layout
    .selectAll(".gridsckh")
    .data(this.hours.data);

  var hour_sc_g = hour_scale
    .enter()
    .append("g")
    .attr("class", "gridsckh");

  hour_sc_g
    .append("line")
    .attr("class", "gridsckhl")
    .merge(hour_scale.select(".gridsckhl"))
    .transition(t)
    .attr("x1", this.mix.gsckh_x1)
    .attr("y1", this.mix.gsckh_y)
    .attr("x2", this.mix.gsckh_x2)
    .attr("y2", this.mix.gsckh_y);

  hour_sc_g
    .append("text")
    .merge(hour_scale.select("text"))
    .transition(t)
    .text(this.mix.gsckh_txt)
    .attr("x", this.mix.gsckh_x2() - 2)
    .attr("y", this.mix.gsckh_y);


  hour_scale.exit().remove();

  this.update_free_text();
};

HourHeader.prototype.create_indicator = function() {

  var hour_scale = this.layout
    .append("rect")
    .attr("x", -40)
    .attr("y", 0)
    .attr("width", 40)
    .attr("height", grid_height())
    .attr("fill", "white");

  this.layout.append("text")
    .attr("id", "exact-time-txt")
    .attr("x", -20)
    .attr("y", -20);

  this.layout.append("line")
    .attr("id", "exact-time-line")
    .attr("x1", 0)
    .attr("x2", 0)
    .attr("y1", 0)
    .attr("y2", 0);

  this.layout
    .on('mouseenter', function() {
      d3.select("#exact-time-line")
        .attr("stroke", "black")
        .attr("stroke-width", 2)
        .attr("x2", grid_width());
    })
    .on('mousemove', function() {
      let m = d3.mouse(this) ;
      let computed_time = cours_reverse_y(m[1]);
      d3.select("#exact-time-txt").text(computed_time) ;
      d3.select("#exact-time-line")
        .attr("y1", m[1])
        .attr("y2", m[1]);
    })
    .on('mouseleave', function() {
      d3.select("#exact-time-txt").text("");
      d3.select("#exact-time-line")
        .attr("stroke-width", 0);
    });
} ;

HourHeader.prototype.update_free_text = function (quick) {
  var t = get_transition(quick);

  let text_group = this.layout
    .selectAll(".gridsckhft")
    .data(this.free_text);

  text_group.exit().remove();

  let new_text_group = text_group
    .enter()
    .append("text")
    .attr("class", "gridsckhft");

  text_group = text_group.merge(new_text_group);

  text_group
    .attr("y", this.mix.gsckh_y_time);


  let texts = text_group
    .selectAll("tspan")
    .data(function(d){ return d.texts; });
  
  texts.exit().remove();

  let new_texts = texts
    .enter()
    .append("tspan")
    .text(function(d) { return d ; });

  texts = texts.merge(new_texts);
  
  texts
    .attr("dy", ".6em")
    .attr("x", -20);
  
};



// Display parameters and functions
function HourMix(settings) {
  this.settings = settings;
  this.gsckh_x1 = function () {
    return 0;
  };
  this.gsckh_x2 = function () {
    return -5;
  };
  this.gsckh_y = function (d) {
    var ret = (d.min - this.settings.day_start_time) * nbRows * scale;
    if (d.hd == 'pm') {
      ret += bknews_h()
        - (this.settings.lunch_break_finish_time
          - this.settings.lunch_break_start_time) * nbRows * scale;
    }
    return ret;
  };
  this.gsckh_txt = function (d) {
    let m = d.min;
    if (m >= 24*60) {
      m -= 24*60;
    }
    let h = Math.floor(m / 60) ;
    m = m - h * 60 ;
    return h + "h" + m.toString().padStart(2, "0");
  };
  this.gsckh_y_time = function(d) {
    return this.gsckh_y(d.time);
  };
}
