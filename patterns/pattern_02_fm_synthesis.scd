/*
3 rhythmic patterns for an FM SynthDef. A main pattern sequeces those 3 patterns
*/

(
~duration = Pseq([0.5, 0.25, 0.3, 0.75, 0.25], 1);
~duration2 = Pseq([0.25, 0.125, 0.15, 0.375, 0.125], 2);
~noteSequence1 = Pseq([50, [48,50,57,65].choose, [48,57,62], 50, 61].midicps, 1);
~noteSequence2 = Pseq([55, 62, [52,57], 55, 65].midicps, 1);
~panPosition = Pseq([0, -0.3, 0.3, -0.4, 0.4], 1);
)

(
SynthDef(\percFM, {
    |carrierFreq = 200, modFreq = 400, panPos = 0, modIndex = 2, amp = 0.2, decay = 0.2|
    var env, modulator, carrier, sound, fm;

    env = EnvGen.kr(Env.perc(0.02, decay), doneAction: 2);

    modulator = SinOsc.ar(modFreq) * modIndex * env;

    carrier = SinOsc.ar(carrierFreq + modulator);

    fm = carrier * env * amp;
    sound = Pan2.ar(fm, panPos);
    Out.ar(0, sound);
}).add;
)

(

TempoClock.default.tempo = 160 / 60;

~pattern1 = Pbind(
    \instrument, \percFM,
    \dur, ~duration,
    \carrierFreq, 400,
    \modFreq, ~noteSequence2,
    \modIndex, Pexprand(0.5, 10, inf),
    \decay, Pwhite(0.2, 0.8, inf),
    \amp, Pseq([0.6, Pexprand(0.1, 0.3, inf), 0.4, 0.6, Pexprand(0.1, 0.5, inf)], 1),
    \panPos, ~panPosition
);

~pattern2 = Pbind(
    \instrument, \percFM,
    \dur, ~duration + 0.5,
    \carrierFreq, ~noteSequence1,
    \modFreq, 750,
    \modIndex, Pexprand(0.5, 10, inf),
    \decay, Pwhite(0.2, 1, inf),
    \amp, Pseq([0.6, Pexprand(0.1, 0.3, inf), 0.4, 0.6, Pexprand(0.1, 0.5, inf)], 1),
	\panPos, ~panPosition * (-1)
);

~pattern3 = Pbind(
    \instrument, \percFM,
    \dur, ~duration2,
    \carrierFreq, 250,
    \modFreq, 750,
    \modIndex, Pexprand(0.5, 10, inf),
    \decay, Pwhite(0.2, 1, inf),
    \amp, Pseq([0.1, Pexprand(0.1, 0.3, inf), 0.4, 0.6, Pexprand(0.1, 0.5, inf)], 1),
	\panPos, ~panPosition * (-1)
);

~mainPattern = Pseq([
	Ppar([~pattern1, [~pattern2, ~pattern3].choose], [1, 2].choose),
    Ppar([~pattern2, [~pattern1, ~pattern3].choose], 2),
	Ppar([~pattern3, [~pattern2, ~pattern1].choose], [1,2].choose)
], inf);
~mainPattern.play;
)