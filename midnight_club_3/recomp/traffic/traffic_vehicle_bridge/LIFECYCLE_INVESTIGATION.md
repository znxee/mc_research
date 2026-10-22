# MC3-0015 lifecycle investigation (2026-10-21)

## Native removal boundary

Alpha PS2 symbol `mcCar::RemoveFromLevel(void)` = 0x2B2AF8.
Recovered source: research/pseudocode/batch_c2f1ca30692ea193.json.
It removes the render/physical instance from phLevel, disables culling,
removes the vehicle manager entry, and sets the removed flag.

Xbox equivalent 0xFFB40 has the same four operations:

* entity+1C -> vehCar, phInst ID at vehCar+8 -> phLevel vtable+14;
* entity+0C+8 -> cullable Enable(false), native 0x92EF0;
* vehManager::Instance 0x3308C0 -> vtable+8 DeleteEntry(entity);
* entity+60 = 1, so the destructor does not delete its manager entry twice.

The recompiler emits 0xFFB40 as an internal label in sub_002BF2A0.
The callable wrapper 0x2BF2A0 loads [ecx+14] then tail-calls 0xFFB40.
Passing the extra owner's mcRacer subobject (owner+C) resolves entity+20.
Do not create a hand-written replacement for the native body just because
sub_000FFB40 has no independent linker symbol.

Extra owners are outside the normal racer count. DestroyCompleteVehicle now
runs this native removal before aiOpponent destructor 0x1EC430, provided the
entity is not already marked removed and its physical ID is live. It is shared
by ambient retirement and manager teardown. Validation is still in progress.

## Immutable failed evidence

* runs/20261021-092110: repeated the prior 052931 C0000005 with identical bad
  guest pointer 06D73114 after returning to frontend; no native removal yet.
* runs/20261021-092411: same late failure with read-only physics diagnostics.
  The first diagnostic was a false positive: some legitimate phInst objects
  live in the image, so a physical-only pointer predicate was inappropriate.
  The checker now uses committed image/guest memory for the instance itself.
* runs/20261021-092730: new native-removal binary; stopped before teardown due
  to a different heap overwrite after the sixth construction. The selected
  pool included repeated vp_d_scion_tc_05, but model causality is unproven.
  Bad header 83A25080 contained 83A25100 / 83A10530; the latter is the new
  vehCar Matrix34. Native vehAutoMgr capacity was already 128. Do not claim
  this is the old component-capacity bug without capturing the new writer.
* runs/20261021-092922: 30 s gameplay with six actors and no bad heap/physics,
  but NO teardown test: a lost Down key selected Change Vehicle. The runner
  now verifies native pause selection using warm/gold pixels. Raw FAIL remains.

A temporary 0x1B3B90 allocation-entry probe walks the heap only while the extra
native Init is running, to report the first damaged allocator boundary and
its guest stack. It is diagnostic, does not repair memory, and should be
removed once the new writer is identified. No speculative slot-ID cap or
reference-count mutation has been installed.

* runs/20261021-093411: six clean constructions and routes; fresh physics
  checker caught id 2161 / node 1035 -> 06D73114 BEFORE the first extra
  destructor, at the old late manager cleanup. All six native removals
  changed live physical IDs to FFFF, but removal at this late boundary is
  insufficient. Testing early release at city shutdown 0x29690, before
  0x6C7F0 ambient teardown, 0x1C11C0 race destruction and 0x2C8970 racer
  singleton shutdown. This run is FAIL; no late-fault suppression is added.

## Confirmed out-of-bounds byte write

`runs/20261021-094431` used a temporary protected-page write watch on the
reproducible damaged record. It captured host RVA BB166C changing pointer
82D73114 -> 06D73114. The installed matching EXE/PDB resolved it to
`__imp__sub_002AD320`, generated x86_recomp.79.cpp line 20370, corresponding
to native 0x2AD433: `mov byte ptr [ebx+ecx],6`.

In that run phLevel+20 (type array) = 828991A0. The damaged pointer's high
byte at 828A919F is exactly type_array + FFFF. Therefore this is an invalid
RemoveEntry(FFFF) writing the removed-state byte 6 outside the array, not a
floating-point, shared-type, shader or material problem. The routine also
writes indices[FFFF] and changes the free-ID count, so repairing the pointer
alone cannot fix it.

Native aiAmbientVehicle cleanup 0x796B0 keeps +AD set while its representation
is active, then removes [ambient+2C] without an FFFF check at 0x7971F. The
bridge detached that phInst earlier to avoid duplicate collision, but retained
the active lane/render object. New scoped hook skips only this already-detached
RemoveEntry when the ambient was detached by this bridge, consumes the one
stdcall argument, and continues at 0x79722. Culling, instance-list and lane
cleanup still run. Detached identities survive extra-owner destruction until
the next native opponent allocation starts a new scene.

The page-protection/VEH watch has been removed from source. A read-only
RemoveEntry entry probe temporarily records any remaining FFFF caller.
`runs/20261021-094156` with the same watch happened to PASS; it did not emit
the bad byte, illustrating why a single menu-return PASS was insufficient.

## First triggered fix validation

`runs/20261021-095405/result.json`: PASS, six complete actors, six native
physical removals/destructions, and 18 s of settled frontend observation.
The scoped guard actually triggered once for ambient 831748B4 at cleanup
0x796B0. No invalid native RemoveEntry, bad physics mapping, heap diagnostic
or exception followed. This is stronger evidence than a PASS where the bad
cleanup path was never taken. A repeated validation is still being run.

`runs/20261021-095126` independently reproduced the Scion-era heap report at
sixth construction and after Reset. Relative damaged-header offset again
was vehCar + 14B60; header words included vehCar + 14BE0 and vehCar + 10.
The original raw FAIL is preserved. A writer has not yet been identified.
Heap snapshots now mirror the native operator new/delete mutex gate
(0x5348EC; enter/leave 0x20DBD0/0x20DBF0). That gate was 0 in 095405, so
no claim of lock-protected snapshots should be inferred for that run.
Per-allocation walking is now opt-in: runner --allocation-probe passes
--mc3-traffic-check-allocations. Default executable avoids that expensive walk.

## 2026-10-21 continued heap audit

`runs/20261021-095634` repeated the heap failure while constructing the fifth
full vehicle. The last clean snapshot was before that Init; the first failed
allocation-entry snapshot was at guest 0x1FAA6B (inside 0x1FA9C0), immediately
after native `operator new(0x24)`. The run stopped because the harness treats
`MC3TRAFFIC heap BAD` as fatal; the log contains no independent guest exception.
Its raw FAIL and `failure_memory/` are preserved. The suspicious address was
again vehCar + 0x14B60 (`839DB9C0` versus car `839C6E60`). The two words there
were pointers, not a plausible heap header. This still does not identify the
writer or prove that the Scion model is the cause.

The native heap walk at 0x1B42A0 uses a payload pointer. At 0x1B435F it moves
that pointer by aligned length + 0x20; at 0x1B42DD the next iteration subtracts
0x10 to get the header. The effective header stride is therefore aligned
length + 0x10, as the original read-only diagnostic used. A trial with +0x20
reported CDCDCDCD in the second block of every car (`runs/20261021-100527`);
that trial was reverted. The diagnostic now also checks each header's masked
backlink against the previous header, as 0x1B4327 does.

Fifteen opt-in setup checkpoints now bracket 0x1FA9C0's allocation and virtual
setup calls. They share the `--mc3-traffic-check-allocations` flag and do not
change native data or control flow. Runs 101107 (six actors, 10 s gameplay,
six native removals, already-detached cleanup triggered once, 23 s frontend),
101330, 101444, 101628 and 101746 (six actors each, 5 s gameplay) passed the
full heap/backlink audit. None reproduced the prior all-Scion template pool;
the writer interval therefore remains unresolved. The current installed binary
contains the scoped RemoveEntry fix plus these dormant diagnostics.
`runs/20261021-101912/result.json` is a current-binary legacy regression PASS:
zero extra vehicles and 18 s of settled frontend observation.

## Exact native heap writer and bounded repair

`runs/20261021-102306` (the intended 600 s soak, raw FAIL during the initial
sixth car) selected four Scion traffic templates. The opt-in checkpoints found
the first bad heap header at `0x1FAA64`, directly after call `0x1FAA5F` to
native `0x121150`. The previous checkpoint at `0x1FAA5D` was clean. The bad
header was 83A0C810; its previous block started 83A0C650, so the previous
block's payload begins 83A0C660. That is the exact 0x1AC-byte object allocated
at `0x1FA9D4`. Native `0x120930` initializes four index words at object
+0x190..+0x19C and three floats at +0x1A0..+0x1A8. `0x121150` appends index
words from the global list without a four-word check. A later append hits
the next heap header at object+0x1B0, where the observed words 0xC/0xD are
plausible sequential indices. This explains the prior car+0x14B60 pattern;
the Scion model is correlated with, but not proven necessary for, overflow.

Installed repair: five scoped hooks on the native index stores in `0x121150`
skip a store only when its target is past object+0x19C during the bridge's own
extra Init. Native scanning, counters and final float assignments still run.
No model is banned and the extra traffic capacity remains six. The first new
binary run `20261021-102822` passed six actors, six removals and 23 s frontend,
but its model pool did not trigger a skipped store. Runs 103047, 103214 and
103333 also passed six constructions without reaching that bound.

`runs/20261021-103926/result.json` is the triggered validation. The sixth
traffic vehicle was `vp_d_scion_tc_05`; the new hook skipped destinations
object+0x1A0 through +0x1B4 (slots 4..9), including the next heap header at
+0x1B0. The full heap walk and backlinks remained valid after Reset, all six
complete vehicles were built, and the 5 s gameplay test passed.

`runs/20261021-104046/result.json` passed a separate 600 s enhanced soak with
this binary and the allocator probe enabled: six complete cars, 366 route
samples per car, physical path lengths up to 10.65 km, maximum route gap
28.11 m, six native physical removals, one scoped duplicate ambient removal,
and 23 s of settled frontend observation after Go to Menus. No heap or physics
diagnostic fired. This pool did not exercise the bounded index hook; the
triggered Scion run above supplies that narrower evidence. A stationary-player
soak does not establish retirement, reuse, or independent Cruise initialization.
