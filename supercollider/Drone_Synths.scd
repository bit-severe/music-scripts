// Two droning synths. One with FM Synthesis and an FFT effect and a second Additive Synth. Also there's a Granular Synth.

(
~duration = Pseq([4.5, 4.25, 4.3, 4.75, 4.25], inf);
~noteSequence1 = Pseq([50, [48,50,57,64].choose, [48,57,62], 50, 61].midicps, inf);
~noteSequence2 = Pseq([55, 62, [52,57], 55, 66].midicps, inf);
~noteSequence3 = Pseq([[50,55], [54,66], [52,57.3], [50,54], [48,52], 59, 61.3, [48,57.1,62]], inf);
~panPosition = Pseq([0, -0.8, 0.8, 0, 0.4], inf);
)

(
SynthDef(\fmSwells, {
    arg carrierFreq = 440, modFreq = 200, modIndex = 1, amp = 0.3, panPos = 0, delayTime = 0.7, feedback = 0.6, attackTime = 0.01, decayTime = 0.5, sustainLevel = 0.5, releaseTime = 1, envelopeType = 0;

    var modulator, carrier, chain, spectralEffect, processedSound, delayedSignal, feedbackSignal, envelope, reverb, sound, output;

    modulator = SinOsc.ar(modFreq) * (carrierFreq * modIndex);

    carrier = SinOsc.ar((carrierFreq * 0.5) + modulator);

    envelope = Select.kr(envelopeType, [
        EnvGen.kr(Env.perc(attackTime, decayTime), doneAction: 2),  // Percussive envelope
        EnvGen.kr(Env.asr(attackTime, sustainLevel, releaseTime), doneAction: 2),  // ASR envelope
        EnvGen.kr(Env([0, 1, 0], [attackTime, decayTime], \sin, releaseTime), doneAction: 2),  // Sine-shaped envelope
        EnvGen.kr(Env.linen(attackTime, sustainLevel, releaseTime, amp), doneAction: 2)  // Linear attack, hold, release
    ]);

    sound = carrier * envelope * amp;

    chain = FFT(LocalBuf(2048), sound);

    spectralEffect = PV_BinScramble(chain, 8);

    // Inverse FFT to convert back to time-domain
    processedSound = IFFT(spectralEffect) * amp;

    delayedSignal = DelayC.ar(processedSound, maxdelaytime: 0.8, delaytime: delayTime);
    feedbackSignal = delayedSignal * feedback;
    processedSound = processedSound + feedbackSignal;

    output = Pan2.ar(processedSound, panPos);

    reverb = FreeVerb.ar(output, 0.8, 0.8, 0.9);

    Out.ar(0, reverb * 0.8);
}).add;


SynthDef(\additiveSynth, {
    arg freq = 440, amp = 0.1, panPos = 0, envDur = 1, waveform = 0, reverbMix = 0.3;

    var env, sineWave1, sineWave2, sineWave3, combinedSineWave, sawFreq, sawWave, sawWave1, combinedSaw, lfoFreq, lfoDepth, lfo, cutoff, filteredSaw, osc, output, reverb;

    env = EnvGen.kr(Env([0, 1, 0], [envDur, envDur], 'sin'), doneAction: 2);

	//var multiplier = rrand(0.8, 2);
    sineWave1 = SinOsc.ar(freq);
    sineWave2 = SinOsc.ar(freq * (3/2));
    sineWave3 = SinOsc.ar(freq * 2.5);
    combinedSineWave = sineWave1 + sineWave2 + sineWave3;

    sawFreq = freq * (1/2);
    sawWave = Saw.ar(sawFreq);
    sawWave1 = Saw.ar(sawFreq * (3/2));
    combinedSaw = sawWave + sawWave1;

    lfoFreq = rrand(0.5, 2);
    lfoDepth = rrand(0.3, 0.5);
    lfo = SinOsc.kr(lfoFreq, 0, lfoDepth, 1);

    cutoff = sawFreq * 3.5 + (lfo * sawFreq * 0.5);
    filteredSaw = RLPF.ar(combinedSaw, cutoff, 0.5);

    osc = Select.ar(waveform, [combinedSineWave, filteredSaw]);

    output = Pan2.ar(osc * (amp * env), panPos);

    reverb = FreeVerb.ar(output, reverbMix, 0.8, 0.5);

    Out.ar(0, reverb * 0.4);
}).add;

SynthDef(\granularSynth, {
    arg bufnum, rate = 1, grainDur = 0.4, amp = 0.1, pan = 0, envDec = 1, releaseTime = 1, freq = 440, impulse = 10, envbuf = -1;
    var grains, env;

    env = EnvGen.kr(Env.linen(0.3, envDec, releaseTime), doneAction: 2);

    grains = GrainSin.ar(numChannels: 2, trigger: Impulse.kr(impulse), dur: grainDur, freq: freq * 2.25, pan: pan, envbufnum: envbuf);

    Out.ar(0, grains * env * amp);
}).add;
)

(
TempoClock.default.tempo = 80 / 60;

~fm = Pbind(
    \instrument, \fmSwells,
    \dur, ~duration,
    \carrierFreq, ~noteSequence1,
    \modFreq, ~noteSequence2,
    \modIndex, Pexprand(0.5, 2, inf),
    \attackTime, Pwhite(1, 4, inf),
    \decayTime, Pwhite(3.5, 6.0, inf),
    \sustainLevel, Pwhite(0.2, 0.8, inf),
    \releaseTime, Pwhite(3, 6.0, inf),
    \envelopeType, Pseq([0, 1, 0, 3, 2, 1, 0, 2, 3, 3], inf),
    \amp, Pseq([0.6, 0.3, 0.4, 0.6, 0.3], inf),
    \panPos, ~panPosition
).play;

~granular = Pbind(
    \instrument, \granularSynth,
    \midinote, ~noteSequence3,
    \impulse, Pwhite(10, 30, inf),
    \grainDur, Pseq([0.5, 0.4, 0.3, 0.5, 0.1], inf),
    \envDec, Pseq([2.5, 2.4, 2.3, 2.6, 2.4], inf),
    \releaseTime, Pwhite(3, 6, inf),
    \amp, Pwhite(0.05, 0.08, inf),
    \pan, ~panPosition * (-1),
    \dur, ~duration,
).play;

~drone = Pbind(
    \instrument, \additiveSynth,
    \dur, ~duration + 4,
    \midinote, ~noteSequence3,
    \waveform, Pseq([1, 0, 0, 1, 0], inf),
    \amp, Pseq([0.7, 0.4, 0.5, 0.7, 0.4], inf),
    \envDur, Pwhite(3.5, 6.0, inf),
    \panPos, ~panPosition * (1/2),
    \reverbMix, Pseq([0.8, Pexprand(0.5, 1, inf), 0.6, 0.8, Pexprand(0.5, 1, inf)], inf)
).play;
)

(
~fm.start();
~granular.start();
~drone.start();
)

(
~fm.stop();
~granular.stop();
~drone.stop();
)