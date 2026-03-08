// Audio feedback utilities for interview states
// Uses Web Audio API to generate subtle tones without external audio files

class AudioFeedbackManager {
  private audioContext: AudioContext | null = null;
  private gainNode: GainNode | null = null;
  
  // Volume settings (keep subtle)
  private readonly volumes = {
    questionEnd: 0.05,
    listeningStart: 0.03,
    processing: 0.04,
    nextQuestion: 0.05,
  };

  private getAudioContext(): AudioContext {
    if (!this.audioContext) {
      this.audioContext = new AudioContext();
      this.gainNode = this.audioContext.createGain();
      this.gainNode.connect(this.audioContext.destination);
    }
    return this.audioContext;
  }

  // Generate a soft beep tone
  private playTone(
    frequency: number,
    duration: number,
    volume: number,
    type: OscillatorType = "sine"
  ): void {
    try {
      const ctx = this.getAudioContext();
      if (!this.gainNode) return;

      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();

      oscillator.type = type;
      oscillator.frequency.setValueAtTime(frequency, ctx.currentTime);

      gainNode.gain.setValueAtTime(0, ctx.currentTime);
      gainNode.gain.linearRampToValueAtTime(volume, ctx.currentTime + 0.05);
      gainNode.gain.linearRampToValueAtTime(0, ctx.currentTime + duration);

      oscillator.connect(gainNode);
      gainNode.connect(this.gainNode);

      oscillator.start(ctx.currentTime);
      oscillator.stop(ctx.currentTime + duration);
    } catch (error) {
      console.warn("Audio feedback error:", error);
    }
  }

  // Question ended - soft descending tone
  questionEnd(): void {
    this.playTone(800, 0.2, this.volumes.questionEnd);
    setTimeout(() => {
      this.playTone(600, 0.15, this.volumes.questionEnd * 0.8);
    }, 100);
  }

  // Listening started - soft ascending tone
  listeningStart(): void {
    this.playTone(400, 0.15, this.volumes.listeningStart);
    setTimeout(() => {
      this.playTone(500, 0.2, this.volumes.listeningStart);
    }, 80);
  }

  // Processing - gentle pulse
  processing(): void {
    this.playTone(300, 0.1, this.volumes.processing, "triangle");
    setTimeout(() => {
      this.playTone(350, 0.1, this.volumes.processing * 0.8, "triangle");
    }, 150);
  }

  // Next question - double beep
  nextQuestion(): void {
    this.playTone(700, 0.1, this.volumes.nextQuestion);
    setTimeout(() => {
      this.playTone(900, 0.15, this.volumes.nextQuestion);
    }, 120);
  }

  // Interview complete - pleasant chord
  interviewComplete(): void {
    this.playTone(523.25, 0.3, 0.05); // C5
    setTimeout(() => {
      this.playTone(659.25, 0.3, 0.05); // E5
    }, 150);
    setTimeout(() => {
      this.playTone(783.99, 0.4, 0.05); // G5
    }, 300);
  }

  // Error - soft low tone
  error(): void {
    this.playTone(200, 0.3, 0.08, "sawtooth");
  }

  // Cleanup
  dispose(): void {
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
      this.gainNode = null;
    }
  }
}

// Singleton instance
export const audioFeedback = new AudioFeedbackManager();

// Hook for using audio feedback in components
export function useAudioFeedback() {
  return audioFeedback;
}

