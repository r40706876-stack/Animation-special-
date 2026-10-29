# V6 visual review — actual proof 40748149982 (2026-10-29 IST)

**Decision: FAIL — full 140-second V6 render is not approved.**

Reviewed the real 14-shot contact sheet and all five six-frame motion strips from the successful V6 proof artifact. This is a visual review, not an inference from green GitHub Actions.

## Observed defects

- Chapters 0–9: many nearly interchangeable medium shots; poor storytelling progression and weak shot variety. Automatic 8×8 perceptual comparison flagged 15 near-duplicate pairs.
- Insect anatomy: both models still read as simplified, rounded toy geometry. Emerald wasp lacks credible narrow waist, wing structure and fine compound-eye detail; roach shell/legs remain conspicuously schematic.
- Chapter 10: a thick foreground tree trunk obscures the burrow/roach action. Chapter 13 has a similarly obstructed ending.
- Chapter 11–12: the white egg/larva reads as a floating blob rather than a believable egg deposited on the cockroach and a growing segmented larva.
- Motion 0: nearly static (measured sampled-frame difference 0.83); 3 and 5 show wing motion but no convincing visible sting contact. Motion 10 preserves the foreground obstruction. Motion 12 shows wasp flight and a white blob but unclear larva development.
- The background is brighter and more populated than V4 but still looks like sparse, regular procedural sticks and flat foliage.

## Changes made in response

- Commit `6ccc9765` and syntax fix `5e89c38`: story-specific camera framing, clearer wide vs macro shots, foreground trunk removal along burrow camera sightlines, repositioned egg and segmented larva.
- Commit `17fdf529`: cancel superseded proof renders rather than spending runner minutes on outdated source.
- Commits `fcd6e9b` and `f395c769`: generate real motion contact strips and auto-audit each completed successful proof run.

## Next verification

- Inspect fresh proof run `40767077776` after completion, not the old stills. The previous successful source run was `40748149982`.
- If new proof still fails, continue targeted anatomy and action animation corrections; do not write `STILL_REVIEW=PASS` or `MOTION_REVIEW=PASS` without a genuine visual pass.
- A successful Blender render or a 24-frame clip decode is **not** a substitute for visual quality approval. Hindi narration listening review and 140-second final decode are later independent gates.

Evidence: [original contact sheet](contact_v6.png), [automatic audit](audit.json), [motion strip folder](motion_strips/).

## Fresh direct visual review — successful proof 40767077776

Reviewed the actual artifact `12854115550` (14 still PNGs, contact sheet and five 24-frame motion MP4s). This is the newer proof, not an assumption from green CI. **Decision remains FAIL.**

- Chapters 2, 3, 5 and 8: oversized pale cockroach dorsal plates and spherical teal wasp sections still resemble toy insects. The white crossing wings look like opaque paddles rather than transparent venated membranes.
- Chapters 0 and 1: the animals are very small relative to the frame; the forest is an open beige floor with repetitive fern ladders and sparse stick trunks.
- Chapters 3 and 5: nearly identical camera angles, no clearly readable stinger-to-body contact in sampled 24-frame motion strips.
- Chapter 10: obstruction is reduced, but the burrow reads as a grey pebble pile; a dark opening is not obvious.
- Chapters 11 and 12: egg and larva are tiny pale marks on the roach while the wasp dominates the shot. Larval development is not visually legible.
- Motion 0: movement is still hard to see in a wide shot; 3/5 have visible wing movement but no convincing sting, 10/12 still lack decisive narrative action.

### New V6.1 corrective pass, pending fresh proof

- Commit `ad666c51`: add a reusable anatomy/story pass with darkened and narrowed roach dorsal plates, a segmented jewel-wasp gaster and petiole, compound-eye facets, animated pointed translucent wings and venation, a dark burrow aperture, and a visible nine-segment larva without an obscuring hovering wasp.
- Commit `7514e1a8`: load the V6.1 pass and give chapters 3/5 distinct sting camera angles and chapters 11/12 tighter egg/larva macro framing.
- Commit `59e12b44`: strengthen the expensive full-render approval gate to fingerprint all dependent Blender scene files, preventing stale visual approvals after anatomical changes.

**Do not approve the full render based on these code changes.** The revised Blender proof still needs to complete and its actual stills and animated motion must be inspected. V4 remains untouched.


## V6.1 proof 40775022479 — inspected directly (2026-10-29 IST)

Source commit: `7514e1a8`. All 20 jobs completed successfully, including 14 stills, five 24-frame motion clips, and the contact assembly. Master artifact `12857675999`. Evidence audit `40781184450` also succeeded and published its contact sheet and motion strips in this folder.

**Decision: FAIL, not approved for the expensive full film.** Direct inspection of `contact_v6.png` and `motion_strips/motion_{0,3,5,10,12}.jpg` showed:
- Chapter 0 and 1: tiny wasp/roach in a huge empty beige clearing; the 24-frame chapter-0 strip is essentially static. Audit sampled-frame difference 0.64.
- Chapters 3 and 5: wing flutter is visible, but the sting needle does not extend or make an unmistakable body contact during the sampled interval. Most movement is in the wings.
- Chapters 7/8/10: similar beige-forest wide compositions, including two near-duplicate image pairs flagged by the audit (7/10 and 8/10).
- Chapter 10: dark burrow entrance not identifiable; the insects are in an ordinary clearing instead of visibly entering an aperture.
- Chapter 12: the larva is more legible, but protruding black antenna/leg rods clutter the macro composition. The forest remains repetitive and both insects still look like simple procedural 3D models, not realistic documentary animals.
- Chapter 13: final wide shot is sparse; the intended departure from the burrow is not visually clear.

### V6.2 targeted corrections (new proof pending)

- Commit `079f82ac`: move the burrow opening beyond the cockroach to keep its dark mouth unobstructed, animate the sting needle through frames 90–121, and hide distracting roach antennae in the larva macro.
- Commit `30e755f5`: give chapter 8 a distinct close-up, reframe chapter 10 on the burrow, reframe chapter 13 on departure, move the first wide shots closer, and animate a short pursuit dart. Sample chapter-0 motion at frames 48–71 and sting at 90–113, instead of static frames.
- `src/jewel_wasp_v6_proof.py` was updated to trigger the next V6 proof run. Its run ID, outcome and actual images **must be verified independently**; no automatic approval is permitted.
- Do not authorize V6 full render until the latest source's 14 stills and all five motion strips are inspected and the actual anatomy, contact, burrow and larva shots are acceptable. V4 remains preserved.


## V6.2 direct visual review — successful proof 40782659283 (2026-10-29 IST)

The 14 actual 540×960 PNG stills and five actual 24-frame MP4 motion proofs were downloaded from artifact `12859863265`, decoded, and inspected as a 14-shot contact sheet and five six-frame motion strips. All 20 jobs passed technical execution. **VISUAL DECISION: FAIL.**

- Automated evidence audit `40788295796` reports 14 stills, 5 clips, 24 frames each, and **five near-duplicate composition pairs** (0/1, 0/7, 0/10, 1/7, 1/10). No automated visual approval.
- Ch 0/1/7/9 are nearly interchangeable sparse wide forest shots; the characters are too small to establish the story.
- Ch 2/3/4/5/8 show bright rounded turquoise wasp sections, pale broad membrane wings and slab-like roach plates; still conspicuously procedural/toy-like rather than documentary-quality insects.
- Sting motion clips 3 and 5 mostly show wing flutter; the actual needle entering the cockroach is not legible in the sampled frames.
- Ch 10 shows a dark flat oval separated from a partially cropped roach, not the cockroach entering a convincing burrow; motion strip shows minimal approach.
- Ch 12 contains detached-looking black leg rods over a creamy segmented larva. The sampled strip shows little larval growth.
- Ch 13 wasp departure is not unmistakable in the still. Forest foliage remains regular, with an open beige ground and a dark empty horizon.

### V6.3 corrections applied, new proof required

- `5bfce908` and `11fc2b54`: new `src/jewel_wasp_v63_story_pass.py` with world-space keyed ovipositor-to-roach contact, closer burrow placement, larva macro cleanup, distinct pursuit/antenna/burrow camera compositions, and removal of accidentally visible wasp anatomy in neural-explanation chapters.
- `ff063fe2`: load the new story pass into the 14-chapter V6 proof scene.
- `7aa440d2`: include the V6.3 story pass in the full-render source-fingerprint approval gate, invalidating stale approvals.
- `2337637e`: proof workflow now watches all upstream scene dependencies and cancels outdated in-progress proofs when newer source is pushed.
- **Do not approve the 140-second render yet.** Inspect the new V6.3 proof stills and motion, and specifically verify a readable sting contact, burrow entry, larva development, less repetitive shots and acceptable insect anatomy. The 140-second V4 film is preserved.


## V6.3 direct review — successful proof 40789821190 (2026-10-29 IST)

Actual current-source proof: all 14 stills and five 24-frame motion jobs succeeded; master artifact `12862799033`. The published `contact_v6.png` and all five `motion_strips/motion_{0,3,5,10,12}.jpg` were inspected visually, not inferred from a green CI check.

**Visual decision: FAIL.** The 14-panel contact still shows a bead-shaped turquoise wasp abdomen, broad slab-like cockroach plates, sparse beige ground, and weakly distinct compositions. Motion 0 shows six nearly indistinguishable positions. Motion 3 and 5 show wing flutter obscuring the needle, with no unmistakable insertion. Chapter 10 shows the cockroach beside a flat black oval rather than walking into a burrow: the hole is behind the roach's local forward-facing head. Chapter 12's larva is recognizable but its six-frame proof is nearly static. The automatic audit's PASS only means 14 images, five decodable 24-frame clips and basic pixel-change checks passed; it is **not** a visual-quality pass.

### V6.4 corrective source changes, fresh proof pending

- `557db0ea`: add `src/jewel_wasp_v64_visual_pass.py` to replace green bead-gaster with a continuous tapered mesh, hide stacked roach plates, darken and populate forest ground, fold wings during sting close-ups, move the camera to show insertion, rotate/animate the roach head-first toward the burrow in chapter 10, enlarge opening pursuit framing and animate larval crawling.
- `e440ed4c`: include V6.4 source in the full-film visual-approval SHA-256 bundle so stale proof approvals cannot authorize an expensive render.
- `4ed561f8` and `a6624690`: watch the V6.4 source and load the new pass in the proof scene; trigger a fresh 14-still/five-motion proof. Its run ID and results must be verified before approving or rendering the full film.

**Full-film approval remains blocked.** Reinspect the real new contact sheet and motion strips, especially needle insertion, roach heading into the hole, larval motion and visual realism. Preserve V4.


## V6.4 actual proof review — run 40796041871 (2026-10-29, 07:19 IST)

The source-specific [proof run](https://github.com/r40706876-stack/Animation-special-/actions/runs/40796041871) completed successfully with 14 still jobs, five animated jobs and contact assembly (20 successful jobs). Master artifact `12865673682`; automated [audit run](https://github.com/r40706876-stack/Animation-special-/actions/runs/40801382782) published the current contact sheet and all five motion strips. I inspected those **actual images** directly. **Visual approval: FAIL.**

- Chapter 0 and 7 stills remain similar (automated audit explicitly flags this pair). The environment is still repetitive, with a dark flat background and conspicuously straight trunks.
- Chapter 3 and 5 motion strips show a nearly stationary turquoise gaster resting on the roach; **no unmistakable stinger insertion** is visible, even though the job decodes and its pixels change.
- Chapter 10 motion strip shows the wasp climbing across the roach but **no burrow mouth** in the sampled frame. The hole is not readable as a real entrance.
- Chapter 12 shows a white larva on the roach, but an isolated large turquoise ellipsoid floats above it. This is the newly created V6.4 gaster, which was added **after** the previous wasp-hide pass. The larval movement remains subtle.
- Anatomical realism remains limited: roach wings resemble two thick leather panels, the wasp has a simplified metallic cylinder, and wings still look synthetic. This is not documentary-quality insect animation.

### V6.5 correction submitted, new proof pending

- Commit `aaded865`: rekeyframe the existing stinger using evaluated wasp and roach world-space transforms, add a timed small contact mark, and focus distinct side-angle cameras on the needle target.
- Move the burrow aperture and its earthen rim into the roach's head-first approach, widen/reframe the chapter-10 camera, and keep its sightline clear.
- Use a distinct high oblique chapter-7 camera to avoid repeating chapter 0.
- Hide **all** wasp descendants after the V6.4 gaster is created in chapter 12, strengthen larval segment undulation, and focus the macro camera.
- `src/jewel_wasp_v64_visual_pass.py` is already watched by the V6 proof workflow, so the push requests a fresh proof without authorizing a full render.

The new V6.5 render must complete, its stills and animated frames must be inspected again, and any remaining realism/action failures corrected before the approval file is written. **No full V6 render authorized. V4 remains unchanged.**


## V6.5 direct inspection — proof 40802877587 (2026-10-29 IST)

The latest source's 14 actual still PNGs and five actual 24-frame MP4 motion proofs were downloaded independently from the 19 completed chapter jobs, even while the contact assembly job was still queued. A manual 14-panel contact sheet and five six-frame motion strips were assembled locally and inspected visually. All 19 chapter jobs passed technical execution; this does **not** establish visual approval.

**Visual decision: FAIL.** Chapters 3/5 still show a teal wasp abdomen pressed against the roach, not a readable penetrating stinger; in the rig the old needle start and target were almost coincident. Chapter 10 shows the wasp standing over a roach, with the dark ground-level burrow hidden beneath them and the entrance obscured by fronds. Chapter 12's larva is finally unobstructed and visible, but its movement remains stylized. Chapter 13 crops the departing wasp at the top-left. Forest floor, foliage, wings and roach plates remain obviously procedural, not documentary quality. No V6 full render authorized.

### V6.6 targeted corrective code — awaiting fresh rendered evidence

- Separate wasp and roach during chapters 3/5, rekeyframe a side-visible copper ovipositor with a real gap and timed insertion, and focus two opposite lateral cameras on the contact.
- Replace the flat chapter-10 oval with an arched vertical black tunnel mouth and earthen mound in front of the roach, clear only the entrance foliage, and animate the roach head-first toward it while the wasp stays off the sightline.
- Sample chapter-10 motion late in the ten-second shot (frames 185–208) to test the actual approach/entry instead of early static setup.
- The new proof must be inspected before further corrections or expensive full render. All prior V4 outputs and V6.5 evidence are preserved.
