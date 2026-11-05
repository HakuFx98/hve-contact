import React from 'react';

export type Expression = 'neutral' | 'happy' | 'shock' | 'smirk';

type Props = {
  x: number;
  y: number; // ground position (feet)
  scale?: number;
  walk?: number; // walk phase in radians; undefined = standing
  skin?: string;
  shirt?: string;
  pants?: string;
  hair?: string;
  hairStyle?: 'short' | 'long' | 'spiky' | 'none';
  expression?: Expression;
  blink?: boolean;
  facing?: 1 | -1;
  armRaise?: number; // 0..1, raises right arm (pointing)
  id: string;
};

// Bobble-head "toy puppet" character: big glossy head, dot eyes,
// capsule body, noodle limbs. Limbs rotate around simple joints.
export const Character: React.FC<Props> = ({
  x,
  y,
  scale = 1,
  walk,
  skin = '#f2c9a5',
  shirt = '#4f7cff',
  pants = '#2b2f4a',
  hair = '#2a1d16',
  hairStyle = 'short',
  expression = 'neutral',
  blink = false,
  facing = 1,
  armRaise = 0,
  id,
}) => {
  const swing = walk === undefined ? 0 : Math.sin(walk) * 28;
  const bob = walk === undefined ? 0 : Math.abs(Math.cos(walk)) * 4;
  const limb = 13;

  const leg = (angle: number, dx: number) => (
    <g transform={`translate(${dx} -70) rotate(${angle})`}>
      <line x1={0} y1={0} x2={0} y2={62} stroke={pants} strokeWidth={limb} strokeLinecap="round" />
      <ellipse cx={6} cy={66} rx={13} ry={7} fill="#1b1b26" />
    </g>
  );

  const arm = (angle: number, dx: number, front: boolean) => (
    <g transform={`translate(${dx} -128) rotate(${angle})`}>
      <line x1={0} y1={0} x2={0} y2={50} stroke={front ? shirt : shade(shirt)} strokeWidth={limb} strokeLinecap="round" />
      <circle cx={0} cy={56} r={9} fill={skin} />
    </g>
  );

  const rightArmAngle = -swing * 0.8 - armRaise * 120;

  return (
    <g transform={`translate(${x} ${y - bob}) scale(${scale * facing} ${scale})`}>
      <defs>
        <radialGradient id={`head-${id}`} cx="35%" cy="30%" r="75%">
          <stop offset="0%" stopColor={lighten(skin)} />
          <stop offset="60%" stopColor={skin} />
          <stop offset="100%" stopColor={shade(skin)} />
        </radialGradient>
        <linearGradient id={`body-${id}`} x1="0" x2="1">
          <stop offset="0%" stopColor={lighten(shirt)} />
          <stop offset="100%" stopColor={shade(shirt)} />
        </linearGradient>
      </defs>
      {/* contact shadow */}
      <ellipse cx={0} cy={bob + 2} rx={44} ry={8} fill="rgba(0,0,0,0.35)" />
      {arm(swing * 0.8, -6, false)}
      {leg(-swing, -10)}
      {leg(swing, 10)}
      {/* torso capsule */}
      <rect x={-26} y={-142} width={52} height={80} rx={24} fill={`url(#body-${id})`} />
      {/* neck */}
      <rect x={-7} y={-158} width={14} height={20} rx={6} fill={shade(skin)} />
      {arm(rightArmAngle, 6, true)}
      {/* head */}
      <g transform="translate(0 -200)">
        {hairStyle === 'long' && <path d="M-46 -6 Q-50 50 -30 58 L30 58 Q50 50 46 -6 Z" fill={hair} />}
        <circle r={48} fill={`url(#head-${id})`} />
        {hairStyle === 'short' && <path d="M-47 -8 Q-44 -52 0 -50 Q44 -52 47 -8 Q30 -30 0 -28 Q-28 -32 -47 -8 Z" fill={hair} />}
        {hairStyle === 'long' && <path d="M-48 0 Q-46 -54 0 -50 Q46 -54 48 0 Q20 -26 -10 -30 Q-34 -26 -48 0 Z" fill={hair} />}
        {hairStyle === 'spiky' && (
          <path d="M-46 -10 L-40 -46 L-24 -36 L-14 -58 L0 -40 L14 -60 L22 -38 L40 -50 L46 -10 Q20 -30 -46 -10 Z" fill={hair} />
        )}
        {/* glossy highlight */}
        <ellipse cx={-16} cy={-22} rx={14} ry={8} fill="rgba(255,255,255,0.28)" transform="rotate(-25 -16 -22)" />
        <Face expression={expression} blink={blink} />
      </g>
    </g>
  );
};

const Face: React.FC<{ expression: Expression; blink: boolean }> = ({ expression, blink }) => {
  const ink = '#1b1530';
  const eyeR = expression === 'shock' ? 7 : 5.5;
  const eyes = blink ? (
    <>
      <line x1={-22} y1={4} x2={-10} y2={4} stroke={ink} strokeWidth={3} strokeLinecap="round" />
      <line x1={14} y1={4} x2={26} y2={4} stroke={ink} strokeWidth={3} strokeLinecap="round" />
    </>
  ) : (
    <>
      <circle cx={-16} cy={4} r={eyeR} fill={ink} />
      <circle cx={20} cy={4} r={eyeR} fill={ink} />
    </>
  );
  const brows: Record<Expression, string> = {
    neutral: 'M-26 -10 Q-16 -14 -6 -10 M10 -10 Q20 -14 30 -10',
    happy: 'M-26 -12 Q-16 -18 -6 -12 M10 -12 Q20 -18 30 -12',
    shock: 'M-26 -18 Q-16 -26 -6 -18 M10 -18 Q20 -26 30 -18',
    smirk: 'M-26 -8 Q-16 -10 -6 -12 M10 -14 Q20 -18 30 -12',
  };
  const mouths: Record<Expression, React.ReactNode> = {
    neutral: <path d="M-8 24 Q2 28 12 24" stroke={ink} strokeWidth={3} fill="none" strokeLinecap="round" />,
    happy: <path d="M-12 20 Q2 36 16 20 Z" fill={ink} />,
    shock: <ellipse cx={2} cy={26} rx={7} ry={9} fill={ink} />,
    smirk: <path d="M-8 26 Q6 28 16 18" stroke={ink} strokeWidth={3} fill="none" strokeLinecap="round" />,
  };
  return (
    <g>
      {eyes}
      <path d={brows[expression]} stroke={ink} strokeWidth={3} fill="none" strokeLinecap="round" />
      {mouths[expression]}
    </g>
  );
};

// tiny color helpers
const adjust = (hex: string, amt: number) => {
  const n = parseInt(hex.slice(1), 16);
  const c = (v: number) => Math.max(0, Math.min(255, v + amt));
  const r = c((n >> 16) & 255);
  const g = c((n >> 8) & 255);
  const b = c(n & 255);
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
};
const shade = (hex: string) => adjust(hex, -40);
const lighten = (hex: string) => adjust(hex, 30);
