# Feature Flag Governance Guide

Nimbus Dynamics feature flag governance, version 1. Owned by Platform Reliability.

## Purpose

Feature flags decouple deploy from release. They exist to control risk, not to hide incomplete work.

## Flag Lifecycle

Every flag is created with an owner, a description, an expiry date, and a removal issue. Flags older than their expiry date generate a weekly cleanup task for the owning team.

## Naming

Flags are named `team.feature.description`, for example `platform.search.new-ranker`. Experimental flags are prefixed with `exp.` and must not gate customer-facing guarantees.

## Defaults

Flags default to off in production. Defaulting a flag on requires architecture-council review, because defaults define what happens when the flag system itself fails.

## Cleanup

Flags are removed within 30 days of full rollout. The cleanup task includes removing dead code paths behind the flag, not just the flag itself.
