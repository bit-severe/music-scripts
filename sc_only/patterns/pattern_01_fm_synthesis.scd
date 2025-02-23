/*
3 rhythmic patterns for an FM SynthDef
*/

(
~duration = Pseq([0.5, 0.25, 0.3, 0.75, 0.25], inf);
~noteSequence1 = Pseq([50, [48,50,57,65].choose, [48,57,62], 50, 61].midicps, inf);
~noteSequence2 = Pseq([55, 62, [52,57], 55, 65].midicps, inf);
~noteSequence3 = Pseq([55, 65, 57.3, 50, 48, 59, 61.3, 57.1].midicps, inf);
~panPosition = Pseq([0, -0.3, 0.3, -0.4, 0.4], inf);
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
TempoClock.default.tempo = 80 / 60;

~fmPattern1 = Pbind(
    \instrument, \percFM,
    \dur, ~duration,
    \carrierFreq, ~noteSequence1,
    \modFreq, ~noteSequence2,
    \modIndex, Pexprand(0.5, 10, inf),
    \decay, Pwhite(0.2, 0.8, inf),
    \amp, Pseq([0.6, Pexprand(0.1, 0.3, inf), 0.4, 0.6, Pexprand(0.1, 0.5, inf)], inf),
    \panPos, ~panPosition
).play;

~fmPattern2 = Pbind(
    \instrument, \percFM,
    \dur, ~duration * 2,
    \carrierFreq, 350,
    \modFreq, 750,
    \modIndex, Pexprand(0.5, 10, inf),
    \decay, Pwhite(0.2, 1, inf),
    \amp, Pseq([0.6, Pexprand(0.1, 0.3, inf), 0.4, 0.6, Pexprand(0.1, 0.5, inf)], inf),
	\panPos, ~panPosition * (-1)
).play;

~fmPattern3 = Pbind(
    \instrument, \percFM,
    \dur, ~duration / 2,
    \carrierFreq, 250,
    \modFreq, 750,
    \modIndex, Pexprand(0.5, 10, inf),
    \decay, Pwhite(0.2, 1, inf),
    \amp, Pseq([0.1, Pexprand(0.1, 0.3, inf), 0.4, 0.6, Pexprand(0.1, 0.5, inf)], inf),
	\panPos, ~panPosition * (-1)
).play;

)