s.options.memSize\_(65536 \* 4);
s.reboot;

(
SynthDef(\filteredSawChord, { |out=0, freq=440, amp=0.3, gate=1, pan=0, modRatio=1, modIndex=100, carrierMultiplier=0.5|

    var env, sig, reverb, modulator, carrier;

    env = EnvGen.kr(Env.adsr(1, 2, 0.8, 9), gate, doneAction: 2);

	modulator = SinOsc.ar(freq _ modRatio) _ (modIndex \* env);

    carrier = SinOsc.ar((freq * carrierMultiplier) + modulator);

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

    Out.ar(out, reverb);

}).add;
)

(
TempoClock.default.tempo = 60 / 60;

Pdef(\fmChordPattern,
	Pfin(24,
		Ppar([
			Pbind(
				\instrument, \filteredSawChord,
				\dur, Pseq([8, 8, 8, 8], inf),
				\legato, 0.3,
				\amp, 0.15, 
    			\freq, Pseq([
    				[-12, 0, 2, 7.2, 14],
    				[-12, 0, 3, 4.8, 12],
    				[-9, 0, 2, 7.2, 10],
    				[-14, -2, 3, 5, 14]
    			], inf).collect(_.midiratio * 440),

    			\carrierMultiplier, Pseq([0.5, 0.75, 0.8],inf),

    			\modRatio, Pexprand(1, 4, inf),
    			\modIndex, Pexprand(10, 300, inf),
    			\pan, Pwhite(-0.8, 0.8, inf),
    		),

    		Pbind(
    			\instrument, \filteredSawChord,
    			\dur, Pseq([8, 8, 8, 8], inf),
    			\legato, 0.3,
    			\amp, 0.08,

    			\baseFreq, Pseq([440 * (6/5), 220 * (3/2), 440 * (4/3)], inf),
    			\freq, Pseq([
    				[-12, 0, 3, 4.8, 12],
    				[-12, 0, 2, 7.2, 14],
    				[-14, -2, 3, 5, 14],
    				[-9, 0, 2, 7.2, 10]
    			], inf).collect{|mr, ev| mr * ev[\baseFreq]},

    			\carrierMultiplier, Pseq([0.5, 0.75, 0.8],inf),
    			\modRatio, Pexprand(1, 4, inf),
    			\modIndex, Pexprand(10, 300, inf),
    			\pan, Pwhite(-0.8, 0.8, inf),
    		)
    	])
    ).play;

)
)
