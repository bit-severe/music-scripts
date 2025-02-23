
(
SynthDef(\amDrone, {
    arg out=0, amp=0.3, carrierFreq=100, modFreq=0.5, modDepth=0.5, pan=0, attack=5, sustain=10, release=5, reverbMix=0.3;

    var carrier, modulator, amSignal, env, reverb, panned;

    env = EnvGen.kr(Env.linen(attack, sustain, release, 1), doneAction: 2);

    modulator = SinOsc.kr(modFreq).range(1 - modDepth, 1 + modDepth);

    carrier = SinOsc.ar(carrierFreq) * modulator;

    amSignal = carrier.tanh * env * amp;

    reverb = FreeVerb.ar(amSignal, mix: reverbMix, room: 0.8, damp: 0.5);

    panned = Pan2.ar(reverb, pan);

    Out.ar(out, panned);
}).add;
)

(
SynthDef(\metallicNoiseScape, {
    arg out=0, amp=0.3, cutoff=400, res=0.98, panRate=0.02, modRate=0.05, modDepth=0.5, metalFreq=800, metalAmt=0.5,
    attack=1, sustain=2, release=3, dur=6, reverbMix=0.5, reverbRoom=0.9, reverbDamp=0.5, panRange=1.0;

    var noise, filterFreq, q, pannedNoise, lfo, panLFO, env, sineTone, metallic, comb, freqShifted, reverb;

    noise = PinkNoise.ar(0.3);

    lfo = SinOsc.kr(modRate, 0, modDepth * cutoff, cutoff);

    q = SinOsc.kr(0.02).range(0.9, res);
    noise = BPF.ar(noise, lfo, q).softclip;

    sineTone = SinOsc.ar(metalFreq, 0, 0.1);

    metallic = noise * SinOsc.ar(metalFreq).range(0.5, 1.5) * metalAmt;

    freqShifted = FreqShift.ar(noise, 100);

    comb = CombN.ar(noise, 0.02, 1 / metalFreq, 2) * 0.3;

    noise = (noise * 0) + (sineTone * 0.2) + (metallic * 0.6) + (freqShifted * 0.2) + (comb * 0.3);

	panLFO = SinOsc.kr(panRate).range(panRange * (-1), panRange);
    pannedNoise = Pan2.ar(noise, panLFO);

    env = EnvGen.kr(Env.linen(attack, sustain, release, 1), doneAction: 2);

    reverb = FreeVerb.ar(pannedNoise, mix: reverbMix, room: reverbRoom, damp: reverbDamp);

	reverb = HPF.ar(reverb, 25);

    Out.ar(out, reverb * env * amp);
}).add;
)

Synth(\metallicNoiseScape, [\cutoff, [1048,250,1857,165].choose, \res, 0.99, \panRate, 0.01, \modRate, [1048,80,857,165].choose, \modDepth, 1, \metalFreq, [1148,1250,1057,1365].choose, \metalAmt, 1, \release, 10, \amp, 1]);

(
TempoClock.default.tempo = 60 / 60;  // Set tempo to 60 BPM
(
Pdef(\noiseScape,
	Pfin(96,
		Ppar([
			Pbind(
				\instrument, \metallicNoiseScape,
				\dur, 6,  
				\attack, Pexprand(0.5, 3, inf),
				\sustain, Pexprand(1, 5, inf),
				\release, Pexprand(4, 9, inf),
				\metalFreq, Pseq([[50, 58, 63], [48,50,57,65].choose, [48,57,62], 46, 61].midicps, inf) * 2,
				\cutoff, Pexprand(300, 1000, inf),
				\modRate, Pexprand(0.01, 0.1, inf),
				\modDepth, Pexprand(0.1, 0.7, inf),
				\panRate, Pexprand(0.01, 0.05, inf),
				\panRange, Pwhite(0.35, 1.0, inf),
				\reverbMix, Pwhite(0.3, 0.7, inf),
				\reverbRoom, Pwhite(0.7, 0.95, inf),
				\reverbDamp, Pwhite(0.2, 0.8, inf),
				\amp, 0.4
			),

			Pbind(
				\instrument, \metallicNoiseScape,
				\dur, 6,  
				\attack, Pexprand(0.5, 3, inf),
				\sustain, Pexprand(1, 5, inf),
				\release, Pexprand(4, 9, inf),
				\metalFreq, Pseq([50, 48, 57, 46, 61].midicps, inf) * 0.5,
				\cutoff, Pexprand(300, 700, inf),
				\modRate, Pexprand(0.01, 0.1, inf),
				\modDepth, Pexprand(0.1, 0.7, inf),
				\panRate, Pexprand(0.01, 0.05, inf),
				\panRange, Pwhite(0.01, 0.3, inf),
				\reverbMix, Pwhite(0.3, 0.7, inf),
				\reverbRoom, Pwhite(0.7, 0.95, inf),
				\reverbDamp, Pwhite(0.2, 0.8, inf),
				\amp, 0.9
			),

			Pbind(
				\instrument, \amDrone,
				\dur, 6,  
				\carrierFreq, Pseq([50, 48, 57, 46, 61].midicps, inf),  
				\modFreq, Pseq([50, 48, 57, 46, 61].midicps, inf) * 0.75,
				\modDepth, 0.9,
				\pan, Pwhite(-0.05, 0.1, inf),
				\attack, Pwhite(1, 3, inf),
				\sustain, Pwhite(5, 5.5, inf),
				\release, Pwhite(5, 7, inf),
				\reverbMix, Pwhite(0.2, 0.7, inf),
				\amp, 0.05
			)
		])
	).play;
)
)
)
