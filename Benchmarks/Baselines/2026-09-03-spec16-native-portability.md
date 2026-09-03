# Part 16 native Linux and Windows qualification

The manually dispatched [native-portability run 33766985023](https://github.com/Matanek/Silex/actions/runs/33766985023)
passed on both Linux X64 and Windows X64 at the exact compiler commit
`f4cae16615ed9e6cd9de19c93b8b2f4adf1d5e6a`. The checkout SHA is present in
both job logs. Dispatch metadata, source hashes, job conclusions and local log
hashes are retained in the [evidence record](2026-09-03-spec16-native-portability.json).

| Target | Runner | Job | Result |
| --- | --- | --- | --- |
| Linux X64 | ubuntu-24.04 | 100687283691 | Passed |
| Windows X64 | windows-2025 | 100687283841 | Passed |

Each target built the compiler with Zig 0.16.0, ReleaseFast and baseline CPU,
then executed 4 string-operator tests, 1 string-return test and 18 native
portability tests. Additional checks executed the Release portability program
with exactly six cycle finalizers, the standalone distribution smoke, and
`AggregateFieldStores.sx` in the interpreter and native Debug/Release. The
smoke and aggregate checks require exact stdout and successful exit status.
These are real native executions, not cross-emission evidence. Local macOS
validation remains recorded with the preceding compiler qualifications.

The user explicitly authorized the named Silex branch push and this workflow.
The first push established its upstream; the follow-up Git audit passed and
local/remote heads were identical. No tag, release, default-branch update,
other repository push or extra workflow was performed.

This closes the previously pending targeted Linux/Windows validation for this
compiler candidate. It does not measure performance on those platforms or
complete Part 16. The latest separate macOS same-layout ratios remain 9.0783
for contact, 29.7626 for integration and 15.9330 for preparation. All still
exceed the required ceiling of 1. Part 16 therefore remains active.
