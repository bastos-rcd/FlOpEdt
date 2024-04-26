# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)




## [1.0.0] -- TO BE RELEASED
This version will include incompatible changes. More specifically:
- the front-end will be refactored and rely on [https://vuejs.org/](`Vue3`)
- the time management will be fundamentally changed to land on standard formats
- the `API` will hence be refactored as well

## [0.5.7] -- 2024-04-26
**Note:** `0.5` is the last `0.*` version.
### Changed
- first celcat export try
- remove passwords in public api
- Debugs:
  * minor fix in configuration

## [0.5.6] -- 2024-02-17
### Changed
- ics with location
- margin between AM and PM when no breaking new declared
- debug solver for transversal groups
- debug limit_time constraints visualization
- add graded in flop!Editor

## [0.5.5] -- 2024-02-06
### Changed
- Debugs:
  * Fix many bugs on 0.5.4 version
  * fix CBC use with time limit on solve_board

## [0.5.4] -- 2024-01-11
### Changed
- Debugs:
  * Docker deployment using makefile
  * Student notifications
  * ics date calculus
  * user_tests decorators
  * include transversal groups in NoGroupCourses constraints
  * various minor bugs in deployment
  * romm availabilities in js HMI
  * ConsiderDependencies pre-analyze

### Added
- Possibility to receive solver log by email after resolution
- Better fileters in LocateAllCourses constraints

## [0.5.3] -- 2023-07-18
### Changed
- Debugs:
  * Debug rooms post_assignment solution_file storage in FlopModel
  * Debug after_type comments in planif_file extraction
  * Debug color assignment
  * crontab command is now working with flop_admin (#72)
  * Consider room constraints in solve_board HMI
  * Debug split_preferences if no departments
  * Consider email_sender parameter (#73)
  * Consider NoTutorCoursesOnDay in visible availabilities

## [0.5.2] -- 2023-06-21
### Changed
- Debugs:
  * Add an [Install] section in systemd unit (#64)
  * Store generated content in a dedicated storage directory and embbed missing XLS files (#65)
  * Change the way /var directories are created and removed in debian package (#67)
  * Embbed missing colors.json file (#68)
  * systemd unit: Daphne listens now on only on 127.0.0.1 with default verbosity (#69)
  * systemd unit: Launch daphne in unbufferized mode in order to have a correct solve board log display (#70)
  * systemd unit: Daphne IP and port are configurable using a system configuration file (#71)
  * optimize the way in which weeks appears in solve_board
  * change color assignation of modules

## [0.5.1] -- 2023-06-05
### Changed
- Debugs:
  - Define correctly directories for constraints generation interface (#59) 
  - Make ALLOWED_HOSTS configurable via flopedt.ini (#60)

## [0.5.0] -- 2023-05-11
### Added
- DevOps
  - pip package
  - debian packages
    - bullseye
    - focal
    - jammy
- `RoomPonderation` objects to allow `TTModel` without room assignation
- `RoomModel` to assign `Rooms`
- Method `reassign_rooms` uses `RoomModel`
- Possibility to pre-assign rooms and/or post-assign rooms in `TTModel`
- Possibility to add a preferred theme in the use's preferences
- Notification system
  - model for backup
  - email notification
  - django-crontab for notification
- `SimultaneousCourses` pre-analyze
- Pre-analyses tests (`ConsiderDependencies`, `ConsiderTutorUnavailabilities`, 
  `NoSimultaneousGroupCourses`, `SimultaneousCourses`)
- `TTConstraints` manager interface: CRUD, dynamic catalog from md files
- `RoomReservation` interface
  - new room attributes
  - reservation types
  - periodicity

### TBD
- right permissions in TTapp/views
- Room preferences: user interface improvement, room exclusion

## [0.4.0] -- 2021-09-07
### Added
- Enable courses with multiple groups
- New app flopeditor: save initial data through graphical interface
  - Departments
  - Rooms (hierarchy, room types)
  - Training programmes
  - Course types
  - Modules
  - Student groups
  - Staff members
- More tutor preferences:
  - mail notification
  - ideal day
  - favorite rooms
- New student preferences design, attributes and behavior
- Module extensive description
- New mode for employees planning
  - new constraints (week-ends, consecutive working hours/days, etc.)
  - batch of weeks
- Modification proposal sent via email
- Enabled text translation, with english, french, spanish, chinese,
  schtroumpf version
- TTApp/ilp_constraints: contains all code + documentation allowing
  to write files in logs that explain the infeasability by the solver
  of a set of constraints
- Availability slots in TTModel to optimize resources
- Wildcard in planification: distributes evenly courses among tutors within a
  module
- the API handles the identification for the modification requests

### Changed
- front-end: dispatch week/day management in js files
- back-end refactoring: all model attributes in english
- Selection of multiple weeks possible with the solve board
- cleaned the API and optimized requests for the mobile application



## [0.3.0] -- 2019-11-07
### Added
- Holidays in solver
- New preferences mode
- More preferences for tutors
- Side panel in main view:
  - Work copy selection
  - Swap versions
  - Reassign rooms
- Side panel in default week view:
  - Change someone else default week
  - Set preferences for each course type, per training programme
- Proposals and transparency checks when course dragging

### Changed
- Bug fixes (slots, rights)
- Import improved


## [0.2.1] -- 2019-07-18
### Added
- Import process:
  - Interface for superusers
  - Pattern configuration file
  - Pattern planification file generation
- Multi-department constraints in the solver

### Changed
- Logo/case


## [0.2.0] -- 2019-02-04
### Added
- Multi-department support
- Solve board improvements:
  - Associated constraints selection
  - Stabilization option based on previous resolution
  - Solver option for production environment
- Satistics view display basic information concerning rooms and tutors

### Changed
- Solver logs are displayed in a fixed size area
- Docker support improvment


## [0.1] -- 2018-11-06
### Added
- Initial features
