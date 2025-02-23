s.boot;
s.waitForBoot {

~coeffs = Array.fill(40, { |i| i + 1 }); // Default to harmonic partials

SynthDef(\synth, {
    arg out=0, freq=440, envType=0, dur=1, gate=1, shift=1.0, phaseModulation =1;
    var env, sig, partials, ampScale;

    env = Select.kr(envType, [
        EnvGen.kr(Env.perc(0.01, dur), doneAction: 2),
        EnvGen.kr(Env.adsr(0.1, 0.2, 0.7, 0.5), doneAction: 2),
        EnvGen.kr(Env.triangle(dur), doneAction: 2),
        EnvGen.kr(Env.sine(dur), doneAction: 2)
    ]);

    //Phase modulation influences the sound significantly. Consider using various phase control functions
    partials = Array.fill(15, { |i|
        var n = i + 1;
        var f = Select.kr(i, ~coeffs);
		var phase = LFNoise1.kr(phaseModulation).range(0, 2pi);
        ampScale = exp(-0.5 * n * shift);
        if (n % 2 == 0) { ampScale = ampScale * 0.8; };
		SinOsc.ar(freq * f, phase, ampScale)
    });

    sig = partials.sum;
	sig = sig * 0.2 * env;

    Out.ar(out, sig!2);
}).add;

OSCdef(\start_recording, { |msg|
   s.record(path: "E:/Samples/supercollider/" ++ msg[1], numChannels: 2);
   "Recording started!".postln;
}, "/start_recording");

OSCdef(\receive_coeffs, { |msg|
    ~coeffs = msg[1..];  // Store coefficients (ignore first OSC element, which is address)
    "Received coefficients: ".postln;
    ~coeffs.postln;
}, "/additive/coeffs");

OSCdef(\synth_control, { |msg, time, addr, recvPort|
    var freq = msg[1];
    var envType = msg[2].asInteger;
	var shift = msg[3];
	var dur = msg[4];
	var phaseModulation = msg[5];

    Synth(\synth,
		[
			\freq, freq,
			\envType, envType,
			\shift, shift,
			\dur, dur,
			\phaseModulation, phaseModulation
		]
	);

}, '/additive/synth');

OSCdef(\stop_recording, { |msg|
    s.stopRecording;
    "Recording saved".postln;
}, "/stop_recording");
};
