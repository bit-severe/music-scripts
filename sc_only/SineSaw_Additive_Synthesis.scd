//  sine waves, filtered saw waves and a set of samples playing endlessly in the key of D

~buffer1 = Buffer.read(s, "shortwave_station_recording.wav");
~buffer2 = Buffer.read(s, "assembly_line.wav");
~buffer3 = Buffer.read(s, "apache.wav");

/*
    3 sine waves are combined given a base frequency. The second sine wave is a fifth 
    above the base and the third is 2.5 times higher than the base frequency.
    2 saw waves are combined given a base frequency which is half the frequency of
    the sine waves. We want the filtered saw waves to have the role of the bass(?).
    The second saw wave is a fifth above the first one. The saw waves are then filtered. 
    This Synth randomly choose between the sine waves and the saw waves, to send to the output. 
    There's also a litlle bit of reverb.       
*/
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

/*
    Just a Synth that plays the loaded samples. Some pitch shifting takes place.
    The buffer index is given to the Synth as an argument, which is later going
    to be used by a Task that will randomly choose between the loaded samples.
    Again, there's some reverb!
*/
SynthDef(\samplePlayback, {
    arg amp = 0.2, panPos = 0, loop = 0, pitchShift = 1, startPos = 0, reverbMix = 0.3, bufferIndex = 0;

    var env = EnvGen.kr(Env([0, 1, 0], [8, 8], 'sin'), doneAction: 2);

    var playbackRate = BufRateScale.kr(bufferIndex) / pitchShift;

    var samplePlayer = PlayBuf.ar(1, bufferIndex, rate: playbackRate, loop: loop, startPos: startPos, doneAction: 2);
    var output = Pan2.ar(samplePlayer * (amp * env), panPos);

    var reverb = FreeVerb.ar(output, reverbMix, 0.9, 0.5);

    Out.ar(0, reverb * 0.3);
}).add;

/*
    A Pluck Synth! There's obviously reverb, but this time
    we also got a delay!
*/
SynthDef(\percussiveAdditive, {
    arg amp = 0.2, panPos = 0, decayTime = 0.5, delayTime = 0.2, feedback = 0.3, freqs = #[440, 550, 660];

    var reverb;

    var env = EnvGen.kr(Env.perc(0.01, decayTime), doneAction: 2);

    var sineWaves = Mix.fill(freqs.size, { |i| SinOsc.ar(freqs[i]) });

    var signal = Pan2.ar(sineWaves * amp * env, panPos);

    var delayedSignal = DelayC.ar(signal, maxdelaytime: 0.8, delaytime: delayTime);  
    var feedbackSignal = delayedSignal * feedback;
    signal = signal + feedbackSignal;

    reverb = FreeVerb.ar(signal, 0.5, 0.9, 0.5);

    Out.ar(0, reverb * 0.5);
}).add;

/*
    The scales here are D3 (base note 50) Major and D3 Mixolydian. It randomly
    chooses between the major and mixolydian. It converts the midi notes to freq
    and randomly chooses a note from the scale. All parameters of the Synth are 
    randomized. The loop waits for 1 to 4 seconds before retriggering the Synth. 
*/
~soundscapeTask = {
Task({
    loop {
        var dMajorDegrees = [0, 1, 4, 5, 7, 9, 11];
        var dMixolydianDegrees = [0, 1, 4, 5, 7, 9, 10];

        var scaleSelect = [0, 1].choose;
        var scaleDegrees = if(scaleSelect == 0, { dMajorDegrees }, { dMixolydianDegrees });
        var scaleNotes = scaleDegrees + 50;
        var scaleFreqs = scaleNotes.collect { |note| note.midicps };

        var freq = scaleFreqs.choose;

		var waitTime;
        var amp = rrand(0.1, 0.4);
        var panPos = rrand(-1.0, 1.0);
        var envDur = rrand(5, 15);
        var waveform = rrand(0, 1).round;  // Randomly choose waveform: 0 for sine, 1 for saw
		var reverbMix = rrand(0.2, 0.9);

		("################## Additive Drone Task log start ##################").postln;
		("Amplitude: " ++ amp).postln;
		("Envelope duration: " ++ envDur).postln;
		("Pan position: " ++ panPos).postln;
		("Waveform: " ++ waveform ++ ". ...(0 for sine, 1 for saw)").postln;
        ("Scale MIDI Note: " ++ freq.cpsmidi).postln;
		("Reverb mix: " ++ reverbMix).postln;

        Synth(\additiveSound,
			[
				\freq, freq,
				\amp, amp,
				\panPos, panPos,
				\envDur, envDur,
				\waveform, waveform,
				\reverbMix, reverbMix
		]);

        waitTime = rrand(1, 4);
        ("Next drone in " ++ waitTime ++ " seconds").postln;
		("################## Additive Drone Task log end ################## \n").postln;
        waitTime.wait;
    }
}).start;
};

/*
    A Task to play the loaded samples. Pitch Shift information are sent to the Synth 
    on each loop. Except for amplitude, all parameters are randomized. 
    The loop waits for 10 to 20 seconds before retriggering the Synth.
*/
~samplePlaybackTask = {
    Task({
        loop {
            var buffers = [
                ~buffer1,
                ~buffer2,
                ~buffer3
            ];

			var waitTime;
			var pitchShift = rrand(-2, 1.2);
            var panPos = rrand(-0.5, 0.5);

            var bufferIndex = rrand(0, buffers.size - 1).round;
            var selectedBuffer = buffers[bufferIndex];

			var startPos = rrand(0, selectedBuffer.numFrames);
			var reverbMix = rrand(0.2, 0.9);
			var loop = [0, 1].choose;

			("################## Sample Playback Task log start ##################").postln;
			("Playing buffer " ++ bufferIndex ++ ", path: " ++ selectedBuffer.path).postln;
			("Start position: " ++ startPos).postln;
			("Pan position: " ++ panPos).postln;
			("Loop sample: " ++ loop).postln;
            ("Pitch Shift: " ++ pitchShift).postln;
			("Reverb mix: " ++ reverbMix).postln;

            Synth(\samplePlayback, [
                \amp, 1,
                \panPos, panPos,
				\pitchShift, pitchShift,
				\startPos, startPos,
                \loop, loop,  // Set to 1 to loop the sample
				\reverbMix, reverbMix,
				\bufferIndex, bufferIndex
            ]);

            waitTime = rrand(10, 20);
            ("Next sample in " ++ waitTime ++ " seconds").postln;
			("################## Sample Playback Task log end ################## \n").postln;
            waitTime.wait;
        }
    }).start;
};

/*
    A Task to trigger the pluck synth. The scale here is D5 Major.
    For the Pluck the number of frequencies (notes) it is going 
    to have on each trigger is a random choise between 3, 5 or 7
    notes playing. As always, all Synth parameters are randomized.
    The loop waits for 4 to 8 seconds before retriggering the Synth.
*/
~percussiveTask = { Task({

	var baseMidi = 74;
    var dMajorScale = [0, 2, 4, 5, 7, 9, 11];

    loop {
		var numberOfFreqs = [3,5,7].choose;
        var freqs = Array.fill(numberOfFreqs, {
            var degree = dMajorScale.choose + baseMidi;
            degree.midicps;
        });
        var amp = rrand(0.1, 0.3);
        var panPos = rrand(-1.0, 1.0);
        var decayTime = rrand(3, 6.5);
		var delayTime = rrand(0.2, 0.8);
		var feedback = rrand(0.5, 0.85);
		var waitTime;

		("################## Pluck Synth Task log start ##################").postln;
		("Number of frequencies: " ++ numberOfFreqs).postln;
		("Selected Notes: " ++ freqs.cpsmidi).postln;

        Synth(\percussiveAdditive, [
            \amp, amp,
            \panPos, panPos,
            \decayTime, decayTime,
			\delayTime, delayTime,
			\feedback, feedback,
			\freqs, freqs
        ]);

        waitTime = rrand(4, 8);
        ("Next pluck in " ++ waitTime ++ " seconds").postln;
		("################## Pluck Synth Task log end ################## \n").postln;
        waitTime.wait;
    }
}).start;
};

~soundscapeTask.();
~samplePlaybackTask.();
~percussiveTask.();