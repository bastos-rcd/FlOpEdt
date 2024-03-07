const intro_confirm_text = gettext('You will erase ALL COURSES corresponding to the following conditions. Do you confirm import ?')

let scheduling_periods_text_pattern = [gettext('From week'), "1" , gettext("year"), current_year, gettext('until week'), 52 , gettext("year"), next_year]
const translated_department = gettext('Department : ');
const translated_training_periods = gettext('Training periods : ');
const translated_scheduling_periods = gettext('Scheduling periods : ');
const translated_all = gettext('All');

let confirm_text = {
    intro : intro_confirm_text,
    department:null,
    training_periods: translated_all,
    scheduling_periods: translated_all}
