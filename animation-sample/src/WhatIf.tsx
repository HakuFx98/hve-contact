import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { Character } from './Character';

const W = 1280;
const H = 720;
const NEON = '#3dffa2'; // luck-green accent
const GOLD = '#f5c451';
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

// ---------- shared bits ----------

const Glow: React.FC = () => (
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="b" />
      <feMerge>
        <feMergeNode in="b" />
        <feMergeNode in="b" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <radialGradient id="vignette" cx="50%" cy="50%" r="75%">
      <stop offset="55%" stopColor="rgba(0,0,0,0)" />
      <stop offset="100%" stopColor="rgba(5,0,20,0.75)" />
    </radialGradient>
  </defs>
);

const Vignette = () => <rect width={W} height={H} fill="url(#vignette)" />;

const blinkAt = (frame: number, offset = 0) => (frame + offset) % 75 < 4;

// Popping number bubble above a head
const LuckTag: React.FC<{ x: number; y: number; value: number; delay: number; color?: string }> = ({
  x,
  y,
  value,
  delay,
  color = NEON,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 9, mass: 0.6 } });
  const float = Math.sin((frame + delay) / 10) * 4;
  return (
    <g transform={`translate(${x} ${y + float}) scale(${s})`} opacity={s > 0.01 ? 1 : 0}>
      <rect x={-46} y={-26} width={92} height={46} rx={23} fill="rgba(10,6,30,0.75)" stroke={color} strokeWidth={3} filter="url(#glow)" />
      <text textAnchor="middle" y={10} fontSize={28} fontWeight={900} fill={color} fontFamily="Inter, Arial, sans-serif">
        🍀{value}
      </text>
    </g>
  );
};

// ---------- Scene 1: hook title ----------

const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop1 = spring({ frame, fps, config: { damping: 8 } });
  const pop2 = spring({ frame: frame - 12, fps, config: { damping: 8 } });
  const shake = frame > 12 && frame < 20 ? Math.sin(frame * 3) * 8 : 0;
  const zoom = interpolate(frame, [0, 100], [1, 1.12]);
  return (
    <AbsoluteFill style={{ background: 'radial-gradient(circle at 50% 45%, #3a1d6e, #0d0624 70%)' }}>
      <svg width={W} height={H}>
        <Glow />
        {Array.from({ length: 60 }).map((_, i) => {
          const sx = (i * 197) % W;
          const sy = (i * 113) % H;
          return <circle key={i} cx={sx} cy={sy} r={1.5 + (i % 3)} fill="#fff" opacity={0.3 + 0.5 * Math.abs(Math.sin((frame + i * 9) / 12))} />;
        })}
        <g transform={`translate(${W / 2 + shake} ${H / 2}) scale(${zoom})`}>
          <text textAnchor="middle" y={-60} fontSize={64} fontWeight={900} fill="#fff" fontFamily="Inter, Arial, sans-serif" transform={`scale(${pop1})`}>
            WHAT IF YOU COULD SEE
          </text>
          <g transform={`translate(0 50) scale(${pop2})`}>
            <text textAnchor="middle" fontSize={110} fontWeight={900} fill={NEON} filter="url(#glow)" fontFamily="Inter, Arial, sans-serif">
              EVERYONE'S LUCK?
            </text>
          </g>
        </g>
        <Vignette />
      </svg>
    </AbsoluteFill>
  );
};

// ---------- Scene 2: school hallway ----------

const Hallway: React.FC = () => {
  const frame = useCurrentFrame();
  const camX = interpolate(frame, [0, 230], [0, -260], { easing: Easing.inOut(Easing.cubic), ...clamp });
  const zoom = interpolate(frame, [130, 160], [1, 1.35], { easing: Easing.out(Easing.cubic), ...clamp });
  const youX = interpolate(frame, [0, 120], [80, 560], clamp);
  const walking = frame < 120;
  const shocked = frame > 130;

  const lockers = Array.from({ length: 22 }).map((_, i) => (
    <g key={i} transform={`translate(${i * 90 - 100} 170)`}>
      <rect width={84} height={300} rx={6} fill={i % 2 ? '#3b3f8f' : '#363a85'} />
      <rect x={10} y={30} width={64} height={8} rx={3} fill="#2a2d6b" />
      <rect x={10} y={46} width={64} height={8} rx={3} fill="#2a2d6b" />
      <rect x={64} y={150} width={8} height={26} rx={3} fill="#9aa0e8" />
    </g>
  ));

  const students = [
    { x: 760, luck: 12, shirt: '#e0566f', hair: 'long' as const, hairC: '#5a2a1a', delay: 40, exp: 'neutral' as const },
    { x: 960, luck: 99, shirt: '#ffb340', hair: 'spiky' as const, hairC: '#ffde59', delay: 70, exp: 'smirk' as const },
    { x: 1160, luck: 47, shirt: '#8a5cff', hair: 'short' as const, hairC: '#111', delay: 95, exp: 'happy' as const },
    { x: 1360, luck: 3, shirt: '#56c2e0', hair: 'short' as const, hairC: '#6b4a2f', delay: 110, exp: 'neutral' as const },
  ];

  return (
    <AbsoluteFill style={{ background: '#1a1240' }}>
      <svg width={W} height={H}>
        <Glow />
        <defs>
          <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#24195a" />
            <stop offset="100%" stopColor="#2f2770" />
          </linearGradient>
          <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#4a3f8c" />
            <stop offset="100%" stopColor="#2a2160" />
          </linearGradient>
        </defs>
        <g transform={`translate(${W / 2} ${H * 0.62}) scale(${zoom}) translate(${-W / 2 + camX} ${-H * 0.62})`}>
          <rect x={-400} y={0} width={3000} height={480} fill="url(#wall)" />
          {/* ceiling lights */}
          {Array.from({ length: 10 }).map((_, i) => (
            <rect key={i} x={i * 260} y={40} width={140} height={14} rx={7} fill="#cfd4ff" opacity={0.8} filter="url(#glow)" />
          ))}
          {lockers}
          <rect x={-400} y={470} width={3000} height={300} fill="url(#floor)" />
          {Array.from({ length: 30 }).map((_, i) => (
            <line key={i} x1={i * 120 - 400} y1={470} x2={i * 160 - 900} y2={720} stroke="rgba(255,255,255,0.06)" strokeWidth={3} />
          ))}
          {students.map((s, i) => (
            <g key={i}>
              <Character id={`st${i}`} x={s.x} y={600} scale={0.95} facing={-1} shirt={s.shirt} hair={s.hairC} hairStyle={s.hair} expression={s.exp} blink={blinkAt(frame, i * 17)} />
              <LuckTag x={s.x} y={330} value={s.luck} delay={s.delay} color={s.luck > 90 ? GOLD : s.luck < 10 ? '#ff5470' : NEON} />
            </g>
          ))}
          <Character id="you" x={youX} y={620} walk={walking ? frame / 3.2 : undefined} shirt="#2ecc8f" expression={shocked ? 'shock' : 'neutral'} blink={blinkAt(frame)} />
          {/* "YOU" marker */}
          <g transform={`translate(${youX} ${360 + Math.sin(frame / 6) * 5})`}>
            <path d="M-14 0 L14 0 L0 18 Z" fill={NEON} filter="url(#glow)" />
            <text y={-10} textAnchor="middle" fontSize={22} fontWeight={900} fill={NEON} fontFamily="Inter, Arial, sans-serif">
              YOU
            </text>
          </g>
          {/* gold sparkle for the 99 guy */}
          {frame > 75 &&
            Array.from({ length: 8 }).map((_, i) => {
              const a = (i / 8) * Math.PI * 2 + frame / 20;
              const r = 70 + Math.sin(frame / 5 + i) * 10;
              return <circle key={i} cx={960 + Math.cos(a) * r} cy={420 + Math.sin(a) * r * 1.4} r={4} fill={GOLD} filter="url(#glow)" />;
            })}
        </g>
        <Vignette />
      </svg>
    </AbsoluteFill>
  );
};

// ---------- Scene 3: explainer card ----------

const Explainer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const card = spring({ frame: frame - 5, fps, config: { damping: 12 } });
  const bar1 = interpolate(frame, [30, 70], [0, 260], { easing: Easing.out(Easing.cubic), ...clamp });
  const bar2 = interpolate(frame, [70, 110], [0, 110], { easing: Easing.out(Easing.cubic), ...clamp });
  const raise = interpolate(frame, [20, 32], [0, 1], clamp);

  const Bar = ({ x, h, label, value, color }: { x: number; h: number; label: string; value: string; color: string }) => (
    <g transform={`translate(${x} 490)`}>
      <rect x={0} y={-h} width={130} height={h} rx={10} fill={color} filter="url(#glow)" />
      <text x={65} y={-h - 16} textAnchor="middle" fontSize={34} fontWeight={900} fill="#fff" fontFamily="Inter, Arial, sans-serif">
        {h > 5 ? value : ''}
      </text>
      <text x={65} y={40} textAnchor="middle" fontSize={22} fill="#d9d4ff" fontFamily="Arial, sans-serif">
        {label}
      </text>
    </g>
  );

  return (
    <AbsoluteFill style={{ background: 'radial-gradient(circle at 60% 40%, #2b1a63, #0b0520 75%)' }}>
      <svg width={W} height={H}>
        <Glow />
        {/* gold-framed serif header */}
        <g transform={`translate(${W / 2 + 120} 110) scale(${card})`}>
          <rect x={-300} y={-50} width={600} height={96} rx={10} fill="#140c33" stroke={GOLD} strokeWidth={4} />
          <rect x={-290} y={-40} width={580} height={76} rx={6} fill="none" stroke={GOLD} strokeWidth={1.5} opacity={0.6} />
          <text textAnchor="middle" y={16} fontSize={46} fill={GOLD} fontFamily="Georgia, 'Times New Roman', serif" fontWeight={700} letterSpacing={4}>
            THE LUCK PARADOX
          </text>
        </g>
        <line x1={540} y1={490} x2={1180} y2={490} stroke="#6b62b8" strokeWidth={3} />
        <Bar x={600} h={bar1} label="Think they're lucky" value="68%" color="#8a5cff" />
        <Bar x={900} h={bar2} label="Actually lucky" value="29%" color={NEON} />
        <Character id="exp" x={260} y={640} scale={1.15} shirt="#2ecc8f" armRaise={raise} expression={frame > 80 ? 'smirk' : 'neutral'} blink={blinkAt(frame, 30)} />
        <Vignette />
      </svg>
    </AbsoluteFill>
  );
};

// ---------- Scene 4: night sky thread ----------

const NightThread: React.FC = () => {
  const frame = useCurrentFrame();
  const tilt = interpolate(frame, [40, 170], [0, 420], { easing: Easing.inOut(Easing.cubic), ...clamp });
  const draw = interpolate(frame, [15, 120], [1, 0], { easing: Easing.inOut(Easing.quad), ...clamp });
  const pulse = 0.7 + 0.3 * Math.sin(frame / 4);
  const threadPath = 'M640 1010 C 560 860, 760 760, 650 600 S 520 380, 700 200 S 800 -20, 640 -260';

  return (
    <AbsoluteFill style={{ background: '#07031a' }}>
      <svg width={W} height={H}>
        <Glow />
        <defs>
          <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#05021a" />
            <stop offset="60%" stopColor="#1c0f4a" />
            <stop offset="100%" stopColor="#3a1f6e" />
          </linearGradient>
        </defs>
        <g transform={`translate(0 ${tilt})`}>
          <rect x={0} y={-500} width={W} height={1700} fill="url(#sky)" />
          {Array.from({ length: 120 }).map((_, i) => (
            <circle key={i} cx={(i * 211) % W} cy={((i * 97) % 1100) - 450} r={1 + (i % 3) * 0.8} fill="#fff" opacity={0.25 + 0.6 * Math.abs(Math.sin((frame + i * 7) / 14))} />
          ))}
          <circle cx={1020} cy={-120} r={60} fill="#fff7d6" filter="url(#glow)" opacity={0.9} />
          {/* building silhouettes */}
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <g key={i}>
              <rect x={i * 230 - 40} y={560 - (i % 3) * 120} width={190} height={600} fill="#120a2e" />
              {Array.from({ length: 12 }).map((_, j) => (
                <rect key={j} x={i * 230 - 20 + (j % 4) * 42} y={590 - (i % 3) * 120 + Math.floor(j / 4) * 60} width={22} height={30} fill={(i + j + Math.floor(frame / 25)) % 5 === 0 ? '#ffd56b' : '#1f1450'} />
              ))}
            </g>
          ))}
          <rect x={0} y={950} width={W} height={300} fill="#0c0722" />
          <path d={threadPath} stroke={NEON} strokeWidth={10 * pulse} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={draw} filter="url(#glow)" />
          <Character id="night" x={640} y={1100} scale={1.3} shirt="#2ecc8f" expression={frame > 60 ? 'happy' : 'shock'} blink={blinkAt(frame, 10)} />
        </g>
        <Vignette />
      </svg>
    </AbsoluteFill>
  );
};

// ---------- Scene 5: outro ----------

const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 9 } });
  const s2 = spring({ frame: frame - 20, fps, config: { damping: 12 } });
  return (
    <AbsoluteFill style={{ background: 'radial-gradient(circle, #2a1660, #0b0520 70%)', justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ transform: `scale(${s})`, fontWeight: 900, fontFamily: 'Inter, Arial, sans-serif', fontWeight: 900, fontSize: 80, color: '#fff', textAlign: 'center', lineHeight: 1.1 }}>
        WHAT WOULD <span style={{ color: NEON, textShadow: `0 0 24px ${NEON}` }}>YOU</span> DO?
      </div>
      <div style={{ opacity: s2, transform: `translateY(${(1 - s2) * 30}px)`, marginTop: 30, fontFamily: 'Arial, sans-serif', fontSize: 34, color: '#d9d4ff' }}>
        Tell me in the comments 👇
      </div>
    </AbsoluteFill>
  );
};

// ---------- captions + HUD (global overlays) ----------

const CAPTIONS: { from: number; to: number; text: string }[] = [
  { from: 5, to: 95, text: 'What if you woke up and could see everyone’s luck?' },
  { from: 105, to: 200, text: 'You walk into school… and numbers pop up over every head.' },
  { from: 205, to: 325, text: 'And then you see it. Ninety-nine. The luckiest person alive.' },
  { from: 335, to: 495, text: 'Here’s the twist: most people think they’re lucky. Most of them are wrong.' },
  { from: 505, to: 675, text: 'But that night, a thread of pure luck shoots out of YOUR chest.' },
];

const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const c = CAPTIONS.find((x) => frame >= x.from && frame <= x.to);
  if (!c) return null;
  const words = c.text.split(' ');
  const perWord = (c.to - c.from - 15) / words.length;
  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 46 }}>
      <div style={{ maxWidth: 1000, textAlign: 'center', fontFamily: 'Inter, Arial, sans-serif', fontWeight: 900, fontSize: 38, lineHeight: 1.25 }}>
        {words.map((w, i) => {
          const on = frame - c.from >= i * perWord;
          const active = on && frame - c.from < (i + 1) * perWord;
          return (
            <span
              key={i}
              style={{
                color: active ? NEON : '#fff',
                opacity: on ? 1 : 0,
                display: 'inline-block',
                margin: '0 7px',
                transform: `scale(${active ? 1.12 : 1})`,
                textShadow: '0 4px 0 #000, 0 0 12px rgba(0,0,0,0.8)',
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Hud: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (frame < 130 || frame > 680) return null;
  const steps = [
    { at: 130, v: 50 },
    { at: 560, v: 77 },
    { at: 600, v: 88 },
    { at: 640, v: 100 },
  ];
  const cur = [...steps].reverse().find((s) => frame >= s.at)!;
  const bump = spring({ frame: frame - cur.at, fps, config: { damping: 7 } });
  const scale = 1 + (1 - bump) * 0.4;
  return (
    <div
      style={{
        position: 'absolute',
        top: 28,
        left: 28,
        padding: '10px 22px',
        borderRadius: 40,
        background: 'rgba(10,6,30,0.65)',
        border: `3px solid ${NEON}`,
        boxShadow: `0 0 20px ${NEON}`,
        fontFamily: 'Inter, Arial, sans-serif', fontWeight: 900,
        fontSize: 32,
        color: '#fff',
        transform: `scale(${scale})`,
        transformOrigin: 'left top',
      }}
    >
      🍀 YOUR LUCK: <span style={{ color: NEON }}>{cur.v}</span>
    </div>
  );
};

// Quick white flash on each hard cut
const CutFlash: React.FC = () => {
  const frame = useCurrentFrame();
  const cuts = [100, 330, 500, 680];
  const d = Math.min(...cuts.map((c) => Math.abs(frame - c)));
  const o = d < 4 ? (4 - d) / 6 : 0;
  return <AbsoluteFill style={{ background: '#fff', opacity: o }} />;
};

export const WhatIf: React.FC = () => (
  <AbsoluteFill style={{ background: '#000' }}>
    <Sequence durationInFrames={100}>
      <Hook />
    </Sequence>
    <Sequence from={100} durationInFrames={230}>
      <Hallway />
    </Sequence>
    <Sequence from={330} durationInFrames={170}>
      <Explainer />
    </Sequence>
    <Sequence from={500} durationInFrames={180}>
      <NightThread />
    </Sequence>
    <Sequence from={680} durationInFrames={90}>
      <Outro />
    </Sequence>
    <Hud />
    <Captions />
    <CutFlash />
  </AbsoluteFill>
);
