<!-- strongly inspired from https://github.com/bchavez/RethinkDb.Driver/blob/master/.github/PULL_REQUEST_TEMPLATE.md -->

## Merge request checklist

Please check if your Merge Request (MR) fulfills the following requirements:
- [ ] We added our names in the `AUTHORS.md` file
- [ ] We added some insights in the `CHANGELOG.md` file
- [ ] New needed python modules have been added to `requirements.txt`, if any
- [ ] Tests for the changes have been added (for bug fixes / features)
- [ ] Docs have been reviewed and added / updated if needed (for bug fixes / features). The wiki page of FlOpEDT may be merge requested as in https://stackoverflow.com/a/38537453
- [ ] No additional printing (neither in django (`print`) or in javascript (`console.log`))


## New dependencies

### Have new dependencies been added?

- [ ] Yes
- [ ] No

If yes, which dependencies?

### Licenses

If new dependencies have been added, their licenses are compatible with the inclusion in a software project licensed under the AGPL version 3.0 or later.

- [ ] Yes indeed.
- [ ] I have looked, but I am not sure. Licensing is such a pain.
- [ ] No, but alternatives exist.

If no, which alternative(s) ?


## Merge request type

<!-- Please try to limit your pull request to one type, submit multiple pull requests if needed. --> 

Please check the type of change your MR introduces:
- [ ] Bugfix
- [ ] Feature
- [ ] Code style update (formatting, renaming)
- [ ] Refactoring (no functional changes, no api changes)
- [ ] Build related changes
- [ ] Documentation contents changes
- [ ] Other (please describe): 


## What is the current behavior?
<!-- Please describe the current behavior that you are modifying, or link to a relevant issue. -->


## What is the new behavior?
<!-- Please describe the behavior or changes that are being added by this MR. -->

-
-
-

## Does this introduce a breaking change?

- [ ] Yes
- [ ] No

<!-- If this introduces a breaking change, please describe the impact for existing applications below. -->


## Does this introduce a new migration in the database ?

- [ ] Yes
- [ ] No


## Other information

<!-- Any other information that is important to this PR such as screenshots of how the component looks before and after the change. -->
