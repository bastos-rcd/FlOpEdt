const intro_confirm_text = gettext('You will erase ALL COURSES corresponding to the following conditions. Do you confirm import ?')

let weeks_text_pattern = [gettext('From week'), "1" , gettext("year"), current_year,
    gettext('until week'), 52 , gettext("year"), next_year]
const translated_department = gettext('Department : ');
const translated_periods = gettext('Periods : ');
const translated_weeks = gettext('Weeks : ');
const translated_all = gettext('All');

let confirm_text = {
    intro : intro_confirm_text,
    department:null,
    periods: translated_all,
    weeks: translated_all}
