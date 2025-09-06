# The Book of CUDA Revelations: Genesis of Kernels

> *In the beginning, there was latency. <br>
> And the GPU God said, “Let there be threads.” And lo, there were 1024 of them. <br>
> And they were good. <br>
> But the memory was not coalesced, and the kernel did crash, and the developer did weep.*<br>

Thus began the journey of the CUDA pilgrim. With trembling fingers and a heart full of hope, she wrote her first bilateral filter. It was fast. It was beautiful. It was broken.

## Day 1: The Awakening
- Installed CUDA toolkit.
- Realized `nvcc` is not a typo.
- Spent 3 hours debugging a missing semicolon.
- Walked in the valley of opencv compilation errors; the angels did cry while Cmake did bare false witness.<br>

## Day 2: The First Filter
- Created a kernel that did... something.
- It ran. It crashed. It ran again and then no more.
- Output was pure NaN. The GPU God was testing her.
- The developer did curse.

## Day 3: The Revelation
- Learned about shared memory.
- Learned to fear shared memory.
- Discovered that performance is a lie unless measured.

## Day 4: The Temptation
- Tried to stack filters.
- The frame rate dropped to 3 FPS (*blasphemy*).
- The developer did wander in the wilderness for a very long time.
- Sacrificed a goat to the profiler.

## Day 5: The Enlightenment
- Found the sweet spot: Diameter 7, Sigma 40, Intensity 70%.
- The video played smoothly. The fans sang. The logs were clean.

## Day 6: The Wrath
- Added a new filter.
- Everything broke.
- The GPU God laughed.
- The developer did curse.

## Day 7: The Rest
- Committed the code.
- Pushed to GitHub.
- Slept like a warrior.

> *And thus the CUDA prophet emerged, not unscathed, but unbroken.<br>
> Her filters ran fast.<br> 
> Her sliders were smooth. <br>
> And her GUI shimmered with translucent gradients.<br>
> The CUDA angels did sing and the developer did rejoice.<br>*


