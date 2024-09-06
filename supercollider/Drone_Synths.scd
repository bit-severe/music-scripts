// Two droning synths. One with FM Synthesis and an FFT effect and a second Additive Synth. 170 BPM for some reason.

(
SynthDef(\fmSwells, {
    arg carrierFreq = 440, modFreq = 200, modIndex = 1, amp = 0.3, panPos = 0, delayTime = 0.7, feedback = 0.6, attackTime = 0.01, decayTime = 0.5, sustainLevel = 0.5, releaseTime = 1, envelopeType = 0;

    var modulator, carrier, chain, spectralEffect, processedSound, delayedSignal, feedbackSignal, envelope, reverb, sound, output;

    modulator = SinOsc.ar(modFreq) * (carrierFreq * modIndex);

    carrier = SinOsc.ar(carrierFreq + modulator);

    envelope = Select.kr(envelopeType, [
        EnvGen.kr(Env.perc(attackTime, decayTime), doneAction: 2),  // Percussive envelope
        EnvGen.kr(Env.asr(attackTime, sustainLevel, releaseTime), doneAction: 2),  // ASR envelope
        EnvGen.kr(Env([0, 1, 0], [attackTime, decayTime], \sin, releaseTime), doneAction: 2),  // Sine-shaped envelope
        EnvGen.kr(Env.linen(attackTime, sustainLevel, releaseTime, amp), doneAction: 2)  // Linear attack, hold, release
    ]);

    sound = carrier * envelope * amp;

    chain = FFT(LocalBuf(2048), sound);

    spectralEffect = PV_BinScramble(chain, 2);

    // Inverse FFT to convert back to time-domain
    processedSound = IFFT(spectralEffect) * amp;

	delayedSignal = DelayC.ar(processedSound, maxdelaytime: 0.8, delaytime: delayTime);
    feedbackSignal = delayedSignal * feedback;
    processedSound = processedSound + feedbackSignal;

    output = Pan2.ar(processedSound, panPos);

	reverb = FreeVerb.ar(output, 0.8, 0.8, 0.9);

    Out.ar(0, reverb * 0.8);
}).add;
)

SynthDef(\additiveSound, {
    arg freq = 440, amp = 0.1, panPos = 0, envDur = 1, waveform = 0, reverbMix = 0.3;

    var env = EnvGen.kr(Env([0, 1, 0], [envDur, envDur], 'sin'), doneAction: 2);

	//var multiplier = rrand(0.8, 2);
	var sineWave1 = SinOsc.ar(freq);
	var sineWave2 = SinOsc.ar(freq * (3/2));
	var sineWave3 = SinOsc.ar(freq * 2.5);
	var combinedSineWave = sineWave1 + sineWave2 + sineWave3;

	var sawFreq = freq * (1/2);
	var sawWave = Saw.ar(sawFreq);
	var sawWave1 = Saw.ar(sawFreq * (3/2));
	var combinedSaw = sawWave + sawWave1;

    var lfoFreq = rrand(0.5, 2);
    var lfoDepth = rrand(0.3, 0.5);
    var lfo = SinOsc.kr(lfoFreq, 0, lfoDepth, 1);

    var cutoff = sawFreq * 3.5 + (lfo * sawFreq * 0.5);
    var filteredSaw = RLPF.ar(combinedSaw, cutoff, 0.5);

    var osc = Select.ar(waveform, [combinedSineWave, filteredSaw]);

    var output = Pan2.ar(osc * (amp * env), panPos);

    var reverb = FreeVerb.ar(output, reverbMix, 0.8, 0.5);

    Out.ar(0, reverb * 0.2);
}).add;

TempoClock.default.tempo = 170 / 60;

~fm = Pbind(
    \instrument, \fmSwells,
    \dur, Pseq([4.5, 4.25, 4.3, 4.75, 4.25], inf),
	\carrierFreq, Pseq([50, [48,50,57,64].choose, [48,57,62], 50, 61].midicps, inf),
    \modFreq, Pseq([55, 62, [52,57], 55, 66].midicps, inf),
    \modIndex, Pexprand(0.5, 2, inf),
	\attackTime, Pwhite(1, 4, inf),
    \decayTime, Pwhite(1.5, 4.0, inf),
    \sustainLevel, Pwhite(0.2, 0.8, inf),
    \releaseTime, Pwhite(1.5, 4.0, inf),
    \envelopeType, Pseq([0, 1, 0, 3, 2, 1, 0, 2, 3, 3], inf),
    \amp, Pseq([0.6, 0.3, 0.4, 0.6, 0.3], inf),
    \panPos, Pwhite(-1, 1, inf)
).play;

~drone = Pbind(
    \instrument, \additiveSound,
    \dur, Pseq([8.5, 8.25, 8.3, 8.75, 8.25], inf),
	\midinote, Pseq([[50,55], [54,66], [52,57.3], [50,54], [48,52], 59, 61.3, [48,57.1,62]], inf),
    \waveform, Pseq([1, 0, 0, 1, 0], inf),
    \amp, Pseq([0.7, 0.4, 0.5, 0.7, 0.4], inf),
	\decayTime, Pwhite(1.5, 4.0, inf),
    \panPos, Pseq([0, -0.4, 0.2, 0, 0.4], inf),
    \reverbMix, Pseq([0.8, Pexprand(0.5, 1, inf), 0.6, 0.8, Pexprand(0.5, 1, inf)], inf)
).play;

~fm.start();
~drone.start();
~fm.stop();
~drone.stop();
