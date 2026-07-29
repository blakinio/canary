# Engine Scheduler behavior model

## Selected source flow

```text
caller thread
  -- addEvent/asyncEvent/scheduleEvent -->
per-thread staged tasks
  -- mergeEvents/mergeAsyncEvents -->
serial, deferred or parallel main queues + scheduled multiset
  -- executeEvents/executeScheduledEvents -->
Task::execute
  -- successful cycle --> Task::updateTime + requeue
  -- completed/canceled/expired --> no execution or reference removal
```

`Dispatcher::init()` runs the dispatch loop through `ThreadPool`. `stopEvent()` nulls the task function and removes the event reference. Dispatcher and ThreadPool shutdown methods reject or stop future work through their selected state paths.

## Separate questions

- Queue structure does not prove equal-time ordering or fairness.
- Mutexes and atomics do not prove race freedom or deadlock safety.
- Due-time comparison does not prove wall-clock accuracy, jitter or cyclic drift.
- Shutdown code presence does not prove draining or cancellation correctness.
- Generic scheduling infrastructure does not prove feature-specific timer behavior.
