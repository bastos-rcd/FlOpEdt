var dsp_svg =
    {
        w: 0,
        h: 0,
        margin: {
            top: 0,     // - TOP BANNER - //
            left: 15,
            right: 0,
            bot: 0
        },
        trans: function () {
            return "translate(" + this.margin.left + "," + this.margin.top + ")";
        }
    };

dsp_svg.cadastre = [
    // weeks ground
    ["svg", "wg"],
    ["wg", "wg-bg"],
    ["wg", "wg-fg"],
];

const dsp_weeks = {
    visible_weeks: 20,
    width: 30,
    height: 30,
    x: 0,      // top of week banner
    y: 0,      // left of week banner
    rad: 1,  // ratio for the radius of prev/next week buttons
    hfac: 0.9, // ratio for week selection ellipse
    wfac: 0.9, // ratio for week selection ellipse
    cont: null,// will be initiated in create_clipweek
};

dsp_svg.h = 40;
dsp_svg.w = (dsp_weeks.visible_weeks + 2) * dsp_weeks.width + dsp_svg.margin.left;

svg = new Svg(true);
svg.create_container();
svg.create_layouts(dsp_svg.cadastre);

// weeks in the current sliding window
const wdw_weeks = new WeeksExcerpt(dsp_weeks.visible_weeks);

let selected_week;

WeekBanner.prototype.apply_wk_change = function (d, i) {
    this.mix.weeks.change_selection(i);

    selected_week = getWeek(d.year, d.week).id;
    filter.by_week(selected_week);
    refreshConstraints();

    this.update(false);
};

wdw_weeks.add_full_weeks(weeks);
const week_banner = new WeekBanner(svg, "wg", "wg-fg", "wg-bg", wdw_weeks, dsp_weeks);
week_banner.spawn();
