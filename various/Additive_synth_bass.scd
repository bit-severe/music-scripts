s.boot;

(
SynthDef(\inharmonicBassRandom, { |out=0, freq=60, amp=0.3, gate=1, shift=1.0, inharm=0.0, cutoff=120|
    var env, sig, partials, chosenFormula, factor, ampScale;

    // Punchy envelope
    env = EnvGen.kr(Env.perc(0.001, 3, 1, curve: -4), gate, doneAction: 2);

    // Define an array of functions for frequency factor formulas
    chosenFormula = [
        { |n, inharm| n + inharm * (n * (n - 1) / 2) },   // Quadratic offset
        { |n, inharm| n * (1 + inharm * (n - 1)) },       // Multiplicative linear offset
        { |n, inharm| n.pow(1 + inharm) },               // Exponential inharmonicity
        { |n, inharm| n + inharm * (n * n - n) },        // Quadratic difference
        { |n, inharm| n + inharm * sqrt(n) },            // Square-root based offset
        { |n, inharm| n + inharm * log(n + 1) }          // Logarithmic offset
    ].choose;  // Randomly choose one formula for this instance of the synth

    // Create 20 partials
    partials = Array.fill(20, { |i|
        var n = i + 1;
        factor = chosenFormula.value(n, inharm);  // Calculate frequency factor
        ampScale = exp(-0.5 * n * shift);  // Amplitude scaling
        if (n % 2 == 0) { ampScale = ampScale * 0.8; };
        SinOsc.ar(freq * factor, 0, ampScale)
    });

    // Sum the partials and apply a lowpass filter
    sig = LPF.ar(partials.sum, cutoff);

    // Apply envelope and output to stereo
    Out.ar(out, (sig * amp * env)!2);
}).add;
)

(
Pbind(
    \instrument, \inharmonicBassRandom,
    \dur, 4,                          // Each event lasts 4 seconds.
	\freq, Pseq([81, 84, 86, 95], inf) * 0.25,
    \amp, 0.5,
    \inharm, Pwhite(0.0, 0.2),          // Random inharmonicity.
    \cutoff, Pexprand(800, 5500, inf)      // Random cutoff values between 80 and 200 Hz.
).play;
)
