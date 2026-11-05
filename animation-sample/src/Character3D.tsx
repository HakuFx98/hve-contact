import React from 'react';

export type Expr = 'neutral' | 'happy' | 'shock';

type Props = {
  position: [number, number, number];
  rotationY?: number;
  walk?: number; // phase in radians; undefined = idle
  skin?: string;
  shirt?: string;
  pants?: string;
  hair?: string;
  hairStyle?: 'short' | 'long' | 'spiky';
  expr?: Expr;
  blink?: boolean;
  scale?: number;
};

const INK = '#15102a';

// Glossy toy "bobble-head" puppet: big sphere head, capsule body, noodle limbs.
export const Character3D: React.FC<Props> = ({
  position,
  rotationY = 0,
  walk,
  skin = '#f2c9a5',
  shirt = '#2ecc8f',
  pants = '#2b2f4a',
  hair = '#2a1d16',
  hairStyle = 'short',
  expr = 'neutral',
  blink = false,
  scale = 1,
}) => {
  const s = walk === undefined ? 0 : Math.sin(walk) * 0.55;
  const bob = walk === undefined ? 0 : Math.abs(Math.cos(walk)) * 0.05;
  const plastic = { roughness: 0.45, metalness: 0.05 };

  const Leg = ({ x, a }: { x: number; a: number }) => (
    <group position={[x, 0.62, 0]} rotation={[a, 0, 0]}>
      <mesh position={[0, -0.25, 0]} castShadow>
        <capsuleGeometry args={[0.075, 0.38, 6, 12]} />
        <meshStandardMaterial color={pants} {...plastic} />
      </mesh>
      <mesh position={[0, -0.52, 0.06]} scale={[1, 0.6, 1.6]} castShadow>
        <sphereGeometry args={[0.09, 16, 12]} />
        <meshStandardMaterial color="#1b1b26" {...plastic} />
      </mesh>
    </group>
  );

  const Arm = ({ x, a }: { x: number; a: number }) => (
    <group position={[x, 1.17, 0]} rotation={[a, 0, x > 0 ? -0.12 : 0.12]}>
      <mesh position={[0, -0.22, 0]} castShadow>
        <capsuleGeometry args={[0.065, 0.32, 6, 12]} />
        <meshStandardMaterial color={shirt} {...plastic} />
      </mesh>
      <mesh position={[0, -0.45, 0]} castShadow>
        <sphereGeometry args={[0.085, 16, 12]} />
        <meshStandardMaterial color={skin} {...plastic} />
      </mesh>
    </group>
  );

  const eyeScale: [number, number, number] = blink ? [1, 0.15, 0.5] : expr === 'shock' ? [1.3, 1.5, 0.5] : [1, 1.25, 0.5];

  return (
    <group position={[position[0], position[1] + bob, position[2]]} rotation={[0, rotationY, 0]} scale={scale}>
      <Leg x={-0.11} a={s} />
      <Leg x={0.11} a={-s} />
      <mesh position={[0, 0.95, 0]} castShadow>
        <capsuleGeometry args={[0.21, 0.32, 8, 16]} />
        <meshStandardMaterial color={shirt} {...plastic} />
      </mesh>
      <Arm x={-0.27} a={-s} />
      <Arm x={0.27} a={s} />
      <mesh position={[0, 1.25, 0]}>
        <cylinderGeometry args={[0.06, 0.07, 0.14, 12]} />
        <meshStandardMaterial color={skin} {...plastic} />
      </mesh>
      {/* head */}
      <group position={[0, 1.62, 0]}>
        <mesh castShadow>
          <sphereGeometry args={[0.42, 48, 32]} />
          <meshStandardMaterial color={skin} roughness={0.35} metalness={0.02} />
        </mesh>
        {/* hair cap */}
        <mesh rotation={[-0.15, 0, 0]}>
          <sphereGeometry args={[0.435, 48, 24, 0, Math.PI * 2, 0, hairStyle === 'long' ? 1.5 : 1.2]} />
          <meshStandardMaterial color={hair} roughness={0.6} />
        </mesh>
        {hairStyle === 'long' && (
          <mesh position={[0, -0.25, -0.12]} scale={[1, 1.1, 0.8]}>
            <sphereGeometry args={[0.42, 32, 16, 0, Math.PI * 2, Math.PI * 0.35, Math.PI * 0.5]} />
            <meshStandardMaterial color={hair} roughness={0.6} side={2} />
          </mesh>
        )}
        {hairStyle === 'spiky' &&
          [-0.24, -0.08, 0.08, 0.24].map((x, i) => (
            <mesh key={i} position={[x, 0.4 - Math.abs(x) * 0.5, -0.05]} rotation={[-0.3, 0, -x * 1.5]}>
              <coneGeometry args={[0.08, 0.24, 12]} />
              <meshStandardMaterial color={hair} roughness={0.6} />
            </mesh>
          ))}
        {/* eyes */}
        {[-0.14, 0.14].map((x) => (
          <mesh key={x} position={[x, 0.02, 0.4]} scale={eyeScale}>
            <sphereGeometry args={[0.042, 16, 12]} />
            <meshStandardMaterial color={INK} roughness={0.2} />
          </mesh>
        ))}
        {/* brows */}
        {[-0.14, 0.14].map((x) => (
          <mesh key={x} position={[x, expr === 'shock' ? 0.17 : 0.12, 0.395]} rotation={[0, 0, Math.PI / 2 + (x > 0 ? -0.15 : 0.15)]}>
            <capsuleGeometry args={[0.012, 0.08, 4, 8]} />
            <meshStandardMaterial color={INK} />
          </mesh>
        ))}
        {/* mouth */}
        {expr === 'shock' ? (
          <mesh position={[0, -0.15, 0.39]} scale={[1, 1.3, 0.4]}>
            <sphereGeometry args={[0.05, 16, 12]} />
            <meshStandardMaterial color={INK} />
          </mesh>
        ) : (
          <mesh position={[0, -0.12, 0.39]} rotation={[0.3, 0, Math.PI]}>
            <torusGeometry args={[expr === 'happy' ? 0.08 : 0.06, 0.014, 8, 24, Math.PI]} />
            <meshStandardMaterial color={INK} />
          </mesh>
        )}
      </group>
    </group>
  );
};
