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


/**************/
/* class Week */
/**************/

function Week(year, week) {
  this.year = year;
  this.week = week;
}

// useful for url generation
Week.prototype.url = function () {
  return this.year + "/" + this.week + "/";
};
Week.prototype.add_to_context = function(context) {
  context['week'] = this.week ;
  context['year'] = this.year ;
};
Week.prototype.as_context = function() {
  return {
    'week': this.week,
    'year': this.year
  };
};

// comparison function
Week.compare = function (week_a, week_b) {
  if (week_a.year < week_b.year) {
    return -1;
  }
  if (week_a.year == week_b.year) {
    if (week_a.week < week_b.week) {
      return -1;
    } else if (week_a.week == week_b.week) {
      return 0;
    }
  }
  return 1;
};

// id function
Week.id_fun = function (week) {
  return "Y" + week.year + "-W" + week.week;
};




/**********************/
/* class WeeksExcerpt */
/**********************/
// desired_nb: target size of the excerpt
// full_weeks: list of weeks forming the full set
// nb: actual size of the excerpt
// first: index in the full list of the first element of the excerpt
// selected: index in the full list of the selected element
// data: list of weeks of the excerpt


function WeeksExcerpt(desired_nb) {
  this.desired_nb = desired_nb;
  this.full_weeks = new Weeks();
  // first and selected undefined until full_weeks is not empty
}

// add weeks to full_weeks
WeeksExcerpt.prototype.add_full_weeks = function (weeks) {
  this.full_weeks.add_all(weeks);
  this.adapt_full_weeks();
  this.first = 0;
  this.selected = 0;
};
// the excerpt should not exceed full weeks size
WeeksExcerpt.prototype.adapt_full_weeks = function () {
  this.nb = Math.min(this.desired_nb, this.full_weeks.get_nb());
};

// getter for the selected index
WeeksExcerpt.prototype.get_iselected = function () {
  return [this.selected];
};
WeeksExcerpt.prototype.get_iselected_pure = function () {
  return this.selected;
};

// getter for the selected week
WeeksExcerpt.prototype.get_selected = function () {
  return this.full_weeks.data[this.selected];
};


// try to go at week chosen, and set the window around
// week: Week
WeeksExcerpt.prototype.chose = function (chosen) {
  var min = this.full_weeks.get_min();
  var max = this.full_weeks.get_max();

  if (Week.compare(min, chosen) > 0) {
    // pick the first week
    this.first = 0;
    this.selected = 0;
  } else if (Week.compare(chosen, max) > 0) {
    // pick the last week
    this.first = this.full_weeks.get_nb() - this.nb;
    this.selected = this.full_weeks.get_nb() - 1;
  } else {
    // pick the first not greater than chosen week
    var not_less = this.full_weeks.data.find(function (week) {
      return Week.compare(week, chosen) >= 0;
    });
    this.selected = this.full_weeks.data.indexOf(not_less);
    this.first = Math.min(this.selected, this.full_weeks.get_nb() - this.nb);
  }
  // extract the data
  this.data = this.full_weeks.data.slice(this.first,
    this.first + this.nb);
};

// move the excerpt data to earlier weeks
WeeksExcerpt.prototype.move_earlier = function () {
  if (this.first > 0) {
    this.first -= 1;
    this.data.pop();
    this.data.unshift(this.full_weeks.data[this.first]);
  }
};

// move the excerpt data to later weeks
WeeksExcerpt.prototype.move_later = function () {
  if (this.first + this.nb < this.full_weeks.get_nb()) {
    this.data.splice(0, 1);
    this.data.push(this.full_weeks.data[this.first + this.nb]);
    this.first += 1;
  }
};

// new selection
WeeksExcerpt.prototype.change_selection = function (shift) {
  if (shift >= 0 && shift < this.nb) {
    this.selected = this.first + shift;
  }
};



/***************/
/* class Weeks */
/***************/
// data: list of Week; all weeks of the school year

// all_weeks: list of {week:,year:}
function Weeks(all_weeks) {
  if (typeof all_weeks === 'undefined') {
    all_weeks = [];
  }
  this.data = [];
  this.add_all(all_weeks);
  this.data.sort(Week.compare);
}

Weeks.prototype.add_all = function (all_weeks) {
  all_weeks.forEach(function (week) {
    this.data.push(new Week(week.year, week.week));
  }, this);
};


Weeks.prototype.get_min = function () {
  return this.data[0];
};

Weeks.prototype.get_max = function () {
  return this.data[this.data.length - 1];
};

Weeks.prototype.get_nb = function () {
  return this.data.length;
};

// add a week indexed by iweek in full_weeks
Weeks.prototype.add_by_index = function (full_weeks, iweek) {
  if (iweek < 0 || iweek >= full_weeks.data.length) {
    return false;
  }
  var week = full_weeks.data[iweek];
  var found = this.data.find(function (d) {
    return Week.compare(d, week) == 0;
  });
  if (typeof found === 'undefined') {
    this.data.push(week);
    return true;
  }
  return false;
};

/********************/
/* class WeekBanner */
/********************/


// svg: Svg
// layout_name: string; name of the layout in the svg
// weeks: WeeksExcerpt
function WeekBanner(svg, layout_name_gen, layout_name_fg, layout_name_bg, weeks, par) {
  this.lay_g = svg.get_dom(layout_name_gen);
  this.lay_fg = svg.get_dom(layout_name_fg);
  this.lay_bg = svg.get_dom(layout_name_bg);
  this.mix = new WeekMix(par, weeks);
  hard_bind(this.mix);
  //this.par.txt_x = this.par.txt_x.bind(this.par) ;
}

//WeekBanner.prototype.

WeekBanner.prototype.spawn = function (full_weeks) {

  this.mix.weeks.chose(new Week(year_init, week_init));

  // shift everything
  this.lay_g
    .attr("transform", this.mix.trans());

  this.lay_fg
    .selectAll(".sel_wk")
    .data(this.mix.weeks.get_iselected())
    .enter()
    .append("g")
    .attr("class", "sel_wk")
    .attr("clip-path", "url(#clipwk)")
    .attr("pointer-events", "none")
    .append("ellipse")
    .attr("cx", this.mix.sel_x)
    .attr("cy", .5 * this.mix.height)
    .attr("rx", .5 * this.mix.wfac * this.mix.width)
    .attr("ry", .5 * this.mix.hfac * this.mix.height);



  var btn_earlier =
    this.lay_fg
      .append("g")
      .attr("class", "cir_wk")
      .on("click", this.week_left.bind(this));

  btn_earlier
    .append("circle")
    .attr("stroke", "white")
    .attr("stroke-width", 1)
    .attr("cx", 0)
    .attr("cy", .5 * this.mix.height)
    .attr("r", this.mix.rad * .5 * this.mix.height);

  btn_earlier
    .append("text")
    .attr("fill", "white")
    .attr("x", 0)
    .attr("y", .5 * this.mix.height)
    .text("<");


  var btn_later =
    this.lay_fg
      .append("g")
      .attr("class", "cir_wk")
      .on("click", this.week_right.bind(this));

  btn_later
    .append("circle")
    .attr("stroke", "white")
    .attr("stroke-width", 1)
    .attr("cx", this.mix.right_sel_x())
    .attr("cy", .5 * this.mix.height)
    .attr("r", this.mix.rad * .5 * this.mix.height);

  btn_later
    .append("text")
    .attr("fill", "white")
    .attr("x", this.mix.right_sel_x())
    .attr("y", .5 * this.mix.height)
    .text(">");


  this.lay_bg
    .append("rect")
    .attr("class", "cir_wk")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", this.mix.strip_w())
    .attr("height", this.mix.height);

  this.lay_bg
    .append("g")
    .append("clipPath")
    .attr("id", "clipwk")
    .append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("height", this.mix.height)
    .attr("width", this.mix.strip_w());

  this.mix.cont = this.lay_bg
    .append("g")
    .attr("clip-path", "url(#clipwk)");


  this.update(true);
};



WeekBanner.prototype.update = function (quick) {

  var t;
  if (quick) {
    t = d3.transition()
      .duration(0);
  } else {
    t = d3.transition()
      .duration(200);
  }

  var sa_wk =
    this.mix.cont
      .selectAll(".rec_wk")
      .data(this.mix.weeks.data, Week.id_fun);

  sa_wk.exit().transition(t).remove();

  var g_wk = sa_wk
    .enter()
    .append("g")
    .attr("class", "rec_wk");

  g_wk
    .merge(sa_wk)
    .on("click", this.apply_wk_change.bind(this));


  g_wk
    .append("rect")
    .attr("y", 0)
    .attr("height", this.mix.height)
    .attr("width", this.mix.width)
    .attr("x", this.mix.rect_x) //rect_wk_init_x)
    .merge(sa_wk.select("rect"))
    .transition(t)
    .attr("x", this.mix.rect_x);

  g_wk
    .append("text")
    .attr("fill", "white")
    .text(this.mix.txt)
    .attr("y", .5 * this.mix.height)
    .attr("x", this.mix.rect_x)
    .merge(sa_wk.select("text"))
    .transition(t)
    .attr("x", this.mix.txt_x);//this.mix.txt_x);

  var wk_sel =
    svg.get_dom("wg-fg")
      .selectAll(".sel_wk")
      .data(this.mix.weeks.get_iselected())
      .select("ellipse")
      .transition(t)
      .attr("cx", this.mix.sel_x);
};


// move timeline to the left
WeekBanner.prototype.week_left = function () {
  this.mix.weeks.move_earlier();
  this.update(false);
};

// move timeline to the right
WeekBanner.prototype.week_right = function () {
  this.mix.weeks.move_later();
  this.update(false);
};


// go to selected week
// Not sure ok even if user is quick (cf fetch_cours)
WeekBanner.prototype.apply_wk_change = function (d, i) { //if(fetch_status.done) {
  this.mix.weeks.change_selection(i);
  dispos = {};
  user.dispos = [];

  fetch_status.course_saved = false;
  fetch_status.pref_saved = false;
  fetch_all(false, true);

  this.update(false);
}; //}


// could be done with prototype and (Object.getPrototypeOf(parameter)
// but simpler to write in this way + there will be a single object

function WeekMix(cst_parameters, weeks) {
  Object.assign(this, cst_parameters);
  this.weeks = weeks;

  this.txt_x = function (d, i) {
    return (i + 1) * this.width;
  };
  this.sel_x = function (d) {
    return (d + 1 - this.weeks.first) * this.width;
  };
  this.trans = function () {
    return "translate(" + this.x + "," + this.y + ")";
  };
  this.right_sel_x = function () {
    return (this.weeks.nb + 1) * this.width;
  };
  this.strip_w = function () {
    return (this.weeks.nb + 1) * this.width;
  };
  this.txt = function (d) {
    return d.week;
  };
  this.rect_x = function (d, i) {
    return (i + 1) * this.width - .5 * this.width;
  };
}

