// Start SuperCollider server
s.boot;

// Define a synth that responds to OSC messages
SynthDef(\py_synth, {
    arg freq = 440, amp = 0.5, dur = 1;
    var env = EnvGen.kr(Env.perc(0.01, dur), doneAction: 2);
    var sig = SinOsc.ar(freq) * amp * env;
	Out.ar(0, [sig, sig]);
}).add;

// Create an OSC listener
OSCdef(\python_control, { |msg, time, addr, recvPort|
    var freq = msg[1];
    var amp = msg[2];
    Synth(\py_synth, [\freq, freq, \amp, amp]);
}, '/synth_control'); // OSC address
