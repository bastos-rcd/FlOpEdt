# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [Unreleased]
### Added
- RoomPonderation objects to allow TTModel without room assignation
- RoomModel to assign Rooms
- Method reassign_rooms uses RoomModel
- Possibility to pre-assign rooms and/or post-assign rooms in TTModel
- Possibility to add a preferred theme in the use's preferences
- Notification system: model for backup, email notification, django-crontab for notification

### Changed

### TBD
- right permissions in TTapp/views
- Room preferences: user interface improvement, room exclusion

## [0.4.0] - 2021-09-07
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



## [0.3.0] - 2019-11-07
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


## [0.2.1] - 2019-07-18
### Added
- Import process:
  - Interface for superusers
  - Pattern configuration file
  - Pattern planification file generation
- Multi-department constraints in the solver

### Changed
- Logo/case


## [0.2.0] - 2019-02-04
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


## [0.1] - 2018-11-06
### Added
- Initial features
