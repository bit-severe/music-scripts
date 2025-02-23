s.boot;
s.waitForBoot {

~cutoffBus = Bus.control(s, 1);
~resonanceBus = 0.5;

SynthDef(\rlpf_synth, {
    arg out = 0, freq = 440, amp = 0.5, envType=0, dur=1, gate = 1, waveType = 0;
    var env, sig, filter, waveform, cutoff, res;

    env = Select.kr(envType, [
        EnvGen.kr(Env.perc(0.01, dur), doneAction: 2),
        EnvGen.kr(Env.adsr(0.1, 0.2, 0.7, 0.5), doneAction: 2),
        EnvGen.kr(Env.triangle(dur), doneAction: 2),
        EnvGen.kr(Env.sine(dur), doneAction: 2)
    ]);

    waveform = Select.ar(waveType, [
        Saw.ar(freq),
        Pulse.ar(freq, 0.5),
        WhiteNoise.ar
    ]);

    cutoff = In.kr(~cutoffBus.index);
    res = ~resonanceBus;

    filter = RLPF.ar(waveform, cutoff, res);

    Out.ar(out, (filter * env * amp) ! 2);

}).add;

OSCdef(\start_recording, { |msg|
    s.record(path: "E:/Samples/supercollider/" ++ msg[1], numChannels: 2);
    "Recording started!".postln;
}, "/start_recording");

OSCdef(\rlpf_synth_control, { |msg, time, addr, recvPort|
    var freq = msg[1];
    var envType = msg[2].asInteger;
    var waveType = msg[3];
    var dur = msg[4];

    Synth(\rlpf_synth,
    	[
    		\freq, freq,
    		\envType, envType,
    		\waveType, waveType,
    		\dur, dur
    	]
    );

}, '/subtractive/rlpfsynth');

OSCdef(\cutoff_control, { |msg|

     ~cutoffBus.set(msg[1]);

}, '/subtractive/global/cutoff');

OSCdef(\resonance_control, { |msg|

     ~resonanceBus = msg[1];

}, '/subtractive/global/resonance');

OSCdef(\stop_recording, { |msg|
`   s.stopRecording;
    "Recording saved".postln;
}, "/stop_recording");
};
