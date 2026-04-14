import { useEffect, useMemo, useState, type CSSProperties } from "react";

function createWavePoints(phase: number, amplitude: number, frequency: number): string {
  const pts: string[] = [];
  for (let x = 0; x <= 100; x += 1) {
    const y = 50 + Math.sin((x / 100) * Math.PI * frequency + phase) * amplitude;
    pts.push(`${x},${y.toFixed(2)}`);
  }
  return pts.join(" ");
}

export type MindState =
  | "reflect"
  | "consolidate"
  | "explore"
  | "practice"
  | "curate"
  | "pursue_goal"
  | "rest"
  | "awakening"
  | "processing"
  | "reflecting"
  | "consolidating";

const STATE_CONFIG: Record<
  MindState,
  {
    phaseStep: number;
    frequencies: [number, number, number];
    amplitudes: [number, number, number];
    coreScale: number;
    breathDuration: number;
  }
> = {
  reflect: {
    phaseStep: 0.031,
    frequencies: [2.25, 3.1, 4.05],
    amplitudes: [11.2, 7.2, 4.6],
    coreScale: 0.97,
    breathDuration: 4.6,
  },
  consolidate: {
    phaseStep: 0.043,
    frequencies: [2.8, 3.8, 4.9],
    amplitudes: [12.9, 8.4, 5.3],
    coreScale: 1.06,
    breathDuration: 3.7,
  },
  explore: {
    phaseStep: 0.026,
    frequencies: [1.95, 2.75, 3.55],
    amplitudes: [10.3, 6.4, 4.1],
    coreScale: 0.94,
    breathDuration: 5,
  },
  practice: {
    phaseStep: 0.036,
    frequencies: [2.45, 3.35, 4.35],
    amplitudes: [11.8, 7.6, 4.8],
    coreScale: 1.01,
    breathDuration: 4.2,
  },
  curate: {
    phaseStep: 0.03,
    frequencies: [2.05, 2.9, 3.75],
    amplitudes: [10.8, 6.9, 4.3],
    coreScale: 0.98,
    breathDuration: 4.8,
  },
  pursue_goal: {
    phaseStep: 0.048,
    frequencies: [3.0, 4.0, 5.0],
    amplitudes: [13.4, 8.7, 5.4],
    coreScale: 1.08,
    breathDuration: 3.5,
  },
  rest: {
    phaseStep: 0.02,
    frequencies: [1.6, 2.2, 2.8],
    amplitudes: [8.8, 5.5, 3.6],
    coreScale: 0.9,
    breathDuration: 5.4,
  },
  awakening: {
    phaseStep: 0.031,
    frequencies: [2.25, 3.1, 4.05],
    amplitudes: [11.2, 7.2, 4.6],
    coreScale: 0.97,
    breathDuration: 4.6,
  },
  processing: {
    phaseStep: 0.043,
    frequencies: [2.8, 3.8, 4.9],
    amplitudes: [12.9, 8.4, 5.3],
    coreScale: 1.06,
    breathDuration: 3.7,
  },
  reflecting: {
    phaseStep: 0.026,
    frequencies: [1.95, 2.75, 3.55],
    amplitudes: [10.3, 6.4, 4.1],
    coreScale: 0.94,
    breathDuration: 5,
  },
  consolidating: {
    phaseStep: 0.036,
    frequencies: [2.45, 3.35, 4.35],
    amplitudes: [11.8, 7.6, 4.8],
    coreScale: 1.01,
    breathDuration: 4.2,
  },
};

type RuntimeMotion = {
  phase: number;
  phaseStep: number;
  freqA: number;
  freqB: number;
  freqC: number;
  ampA: number;
  ampB: number;
  ampC: number;
  coreScale: number;
  breathDuration: number;
};

type Props = {
  mindState?: MindState;
};

export function HeroWave({ mindState }: Props) {
  const [state, setState] = useState<MindState>(mindState ?? "reflect");
  const [motion, setMotion] = useState<RuntimeMotion>(() => {
    const init = STATE_CONFIG.reflect;
    return {
      phase: 0,
      phaseStep: init.phaseStep,
      freqA: init.frequencies[0],
      freqB: init.frequencies[1],
      freqC: init.frequencies[2],
      ampA: init.amplitudes[0],
      ampB: init.amplitudes[1],
      ampC: init.amplitudes[2],
      coreScale: init.coreScale,
      breathDuration: init.breathDuration,
    };
  });

  useEffect(() => {
    if (mindState) {
      setState(mindState);
    }
  }, [mindState]);

  useEffect(() => {
    if (mindState) return;
    const states: MindState[] = [
      "reflect",
      "consolidate",
      "explore",
      "practice",
      "curate",
      "pursue_goal",
      "rest",
    ];
    let idx = 0;

    const stateTimer = window.setInterval(() => {
      idx = (idx + 1) % states.length;
      setState(states[idx]);
    }, 14000);

    return () => window.clearInterval(stateTimer);
  }, [mindState]);

  useEffect(() => {
    let raf = 0;
    let lastTs = performance.now();

    const tick = (now: number) => {
      const dt = Math.min(2.2, (now - lastTs) / 16.67);
      lastTs = now;

      setMotion((prev) => {
        const target = STATE_CONFIG[state];
        const lerp = 1 - Math.pow(0.968, dt);
        const nextPhaseStep = prev.phaseStep + (target.phaseStep - prev.phaseStep) * lerp;

        return {
          phase: prev.phase + nextPhaseStep * dt,
          phaseStep: nextPhaseStep,
          freqA: prev.freqA + (target.frequencies[0] - prev.freqA) * lerp,
          freqB: prev.freqB + (target.frequencies[1] - prev.freqB) * lerp,
          freqC: prev.freqC + (target.frequencies[2] - prev.freqC) * lerp,
          ampA: prev.ampA + (target.amplitudes[0] - prev.ampA) * lerp,
          ampB: prev.ampB + (target.amplitudes[1] - prev.ampB) * lerp,
          ampC: prev.ampC + (target.amplitudes[2] - prev.ampC) * lerp,
          coreScale: prev.coreScale + (target.coreScale - prev.coreScale) * lerp,
          breathDuration:
            prev.breathDuration + (target.breathDuration - prev.breathDuration) * lerp,
        };
      });

      raf = window.requestAnimationFrame(tick);
    };

    raf = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(raf);
  }, [state]);

  const waveA = useMemo(
    () => createWavePoints(motion.phase, motion.ampA, motion.freqA),
    [motion.ampA, motion.freqA, motion.phase],
  );
  const waveB = useMemo(
    () => createWavePoints(motion.phase + 1.2, motion.ampB, motion.freqB),
    [motion.ampB, motion.freqB, motion.phase],
  );
  const waveC = useMemo(
    () => createWavePoints(motion.phase + 2.4, motion.ampC, motion.freqC),
    [motion.ampC, motion.freqC, motion.phase],
  );

  const coreStyle = {
    "--core-scale": motion.coreScale.toFixed(3),
    "--breath-duration": `${motion.breathDuration.toFixed(2)}s`,
  } as CSSProperties;

  return (
    <section className="panel hero-wave-panel">
      <div className="hero-header">
        <p className="kicker">CONSCIOUSNESS LIVE</p>
        <h1>Continuous Digital Life</h1>
        <p className="subtitle">Reverie keeps thinking when the world goes silent.</p>
      </div>

      <div className={`wave-stage state-${state}`}>
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="wave-svg" aria-hidden>
          <polyline className={`wave wave-c state-${state}`} points={waveC} />
          <polyline className={`wave wave-b state-${state}`} points={waveB} />
          <polyline className={`wave wave-a state-${state}`} points={waveA} />
        </svg>
        <div className={`core-orb state-${state}`} style={coreStyle} aria-hidden>
          <div className="core-orb-inner" />
        </div>
      </div>

      <p className="mind-state">mind-state: {state}</p>
    </section>
  );
}
