s.options.memSize_(65536 * 4);
s.reboot;

(
SynthDef(\filteredSawChord, { |out=0, freq=440, amp=0.3, gate=1, pan=0, modRatio=1, modIndex=100, carrierMultiplier=0.5|
    var env, sig, reverb, modulator, carrier;

    // ADSR Envelope for dynamic shaping
    env = EnvGen.kr(Env.adsr(1, 2, 0.8, 9), gate, doneAction: 2);

   // Modulator (creates sidebands)
    modulator = SinOsc.ar(freq * modRatio) * (modIndex * env);

    // Carrier wave (modulated by the modulator)
	carrier = SinOsc.ar((freq * carrierMultiplier) + modulator);

    // Apply amplitude envelope and panning
    sig = Pan2.ar(carrier * env * amp, pan);

	reverb = JPverb.ar(
        sig,
        \t60.kr(1,           0.05),
        \damp.kr(0,          0.05),
        \size.kr(1,          0.05),
        \earlydiff.kr(0.707, 0.05),
        \mdepth.kr(5,        0.05),
        \mfreq.kr(2,         0.05),
        \lowx.kr(1,          0.05),
        \midx.kr(1,          0.05),
        \highx.kr(1,         0.05),
        \lowband.kr(500,     0.05),
        \highband.kr(2000,   0.05)
    );

    // Send to output
    Out.ar(out, reverb);
}).add;
)


(
TempoClock.default.tempo = 60 / 60;  // Set tempo to 60 BPM

Pdef(\fmChordPattern,
	Pfin(24,   // Limit to 24 events (chords)
		Ppar([
			Pbind(
				\instrument, \filteredSawChord,
				\dur, Pseq([8, 8, 8, 8], inf),  // Each chord lasts 8 beats
				\legato, 0.3,                   // Sustain most of the beat
				\amp, 0.15,                      // Reduce volume to prevent clipping

				// Fix: Apply midicps correctly
				\freq, Pseq([
					[-12, 0, 2, 7.2, 14],
					[-12, 0, 3, 4.8, 12],
					[-9, 0, 2, 7.2, 10],
					[-14, -2, 3, 5, 14]
				], inf).collect(_.midiratio * 440),

				\carrierMultiplier, Pseq([0.5, 0.75, 0.8],inf),

				// Randomize modulation ratios
				\modRatio, Pexprand(1, 4, inf),  // Weird frequency ratios
				\modIndex, Pexprand(10, 300, inf), // Different levels of FM complexity

				// Spread notes across the stereo field
				\pan, Pwhite(-0.8, 0.8, inf),
			),

			Pbind(
				\instrument, \filteredSawChord,
				\dur, Pseq([8, 8, 8, 8], inf),  // Each chord lasts 8 beats
				\legato, 0.3,                   // Sustain most of the beat
				\amp, 0.08,                      // Reduce volume to prevent clipping

				\baseFreq, Pseq([440 * (6/5), 220 * (3/2), 440 * (4/3)], inf),

				// Fix: Apply midicps correctly
				\freq, Pseq([
					[-12, 0, 3, 4.8, 12],
					[-12, 0, 2, 7.2, 14],
					[-14, -2, 3, 5, 14],
					[-9, 0, 2, 7.2, 10]
				], inf).collect{|mr, ev| mr * ev[\baseFreq]},

				\carrierMultiplier, Pseq([0.5, 0.75, 0.8],inf),

				// Randomize modulation ratios
				\modRatio, Pexprand(1, 4, inf),  // Weird frequency ratios
				\modIndex, Pexprand(10, 300, inf), // Different levels of FM complexity

				// Spread notes across the stereo field
				\pan, Pwhite(-0.8, 0.8, inf),
			)
		])
	).play;
)
)

