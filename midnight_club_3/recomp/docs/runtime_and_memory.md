# Runtime, threads and memory

## Guest threads need a process block

- **Symptom:** an intermittent crash in the audio thread (guest 0x1B15D0) while a
  race loads. The crash came from `XSetProcessQuantumLength` (0x1354A) writing through
  a null pointer.
- **Cause:** every guest thread's `KTHREAD` must point at a process block in
  `ApcState.Process` (offset +0x44). The runtime never filled it, and recycled
  thread blocks were not cleared, so their fields held stale values.
- **Fix:** `runtime/kernel/threads.cpp` creates one process block (thread quantum 60,
  base priority 8) and points every thread at it. The KPCR and ETHREAD blocks are
  zeroed before use. The fix applies to every game the runtime runs.

## 128 MB guest memory (optional)

- Enabled with `--mc3-guest-memory=128` or `guest_memory_mb = 128` in
  `settings.toml`. The default stays at 64 MB.
- **Mapping more memory does not enlarge the game's heap by itself.** The heap is a
  constant 47 MB: the code at 0x12440 pushes 0x2F, which goes through
  `sub_002698C0` to `XPhysicalAlloc`. A hook on `sub_002698C0` in `hooks.cpp` adds the
  64 MB extra, for 111 MB.
- Heap fields: +0x0C is the capacity, +0x10 the amount used, which grows on demand.
  The log's `bit0clear` counts only holes; the real free space is `untouched=`.
- With 128 MB, the top blocks pass 0x84000000. Address checks must use
  `mem::PhysicalEnd()`, never the constant `0x84000000`.
- Test density of traffic with `--guest-memory 128` in `probe_arcade_traffic.py`.

## Debugging tips

- **Before blaming the heap**, look for another fixed list that appends without a
  bound check. The pattern to search for is `{ptr, cap u16, count u16}`. Several
  "out of memory" failures in the traffic work were fixed lists, not the heap.
- `--mc3-write-watch` sets DR0 on a location and logs the writer and the guest stack.
- A minidump with dbghelp gives the host instruction pointer of a crash.
- `render_ab/xbe_dis.py <address> --func` disassembles a function of `default.xbe`.
- Log lines written with `LOGI` are filtered out of release logs. Use `LOGE` or `LOGR`.
