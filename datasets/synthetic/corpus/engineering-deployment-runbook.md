# Deployment Runbook

Nimbus Dynamics deployment runbook, version 7. Owned by Platform Reliability.

## Preconditions

All CI checks pass. The feature flag for the change exists and is defaulted off. The owning team has confirmed a rollback plan.

## Steps

1. Announce the deploy window in the operations channel.
2. Run the release pipeline for the staging environment and verify smoke tests.
3. Promote the same artifact to production. Never rebuild between environments.
4. Enable the feature flag for an internal test cohort and verify behavior.
5. Roll out to 10 percent of traffic, then 50 percent, then 100 percent, watching error budgets.
6. If error rate rises 0.5 percent above baseline for 10 minutes, disable the flag and file an incident.

## Rollback

Feature flags revert instantly. Database migrations must be forward-compatible; the runbook forbids destructive migrations in the same release as code changes.

## Post-Deploy

The owning team updates the release log and closes the announce thread within one business day.
