import React, { useMemo } from 'react';
import { Decal, Outlines } from '@react-three/drei';
import * as THREE from 'three';

/* ------------------------------------------------------------------
 * Stylised hoodie character:
 *  - big smooth pale head with a 2D-drawn face (decal)
 *  - thick dark outlines (inverted hull)
 *  - hoodie with hood, drawstrings and pocket
 *  - stick-thin legs + neck, ball hands
 * ------------------------------------------------------------------ */

export type Face = 'smug' | 'happy' | 'open' | 'shock' | 'dizzy';
export type Pose = 'idle' | 'cheer' | 'fists' | 'wave';

const LINE = '#1d1430';
const BODY = '#efe9f6'; // pale lilac-white
const OUT = 0.018; // outline thickness

const Mat: React.FC<{ color: string; rough?: number }> = ({ color, rough = 0.55 }) => (
  <meshStandardMaterial color={color} roughness={rough} metalness={0} />
);

/** Face drawn on a transparent canvas, then projected onto the head. */
const useFace = (face: Face, blink: boolean) =>
  useMemo(() => {
    const c = document.createElement('canvas');
    c.width = c.height = 512;
    const g = c.getContext('2d')!;
    g.strokeStyle = LINE;
    g.fillStyle = LINE;
    g.lineWidth = 16;
    g.lineCap = 'round';
    const L = 170;
    const R = 342;
    const Y = 230;
    const arcUp = (x: number) => {
      g.beginPath();
      g.arc(x, Y + 18, 34, Math.PI * 1.15, Math.PI * 1.85);
      g.stroke();
    };
    const dot = (x: number, rx = 20, ry = 30) => {
      g.beginPath();
      g.ellipse(x, Y, rx, ry, 0, 0, Math.PI * 2);
      g.fill();
    };
    const closed = (x: number) => {
      g.beginPath();
      g.moveTo(x - 30, Y + 4);
      g.lineTo(x + 30, Y + 4);
      g.stroke();
    };

    if (blink && face !== 'happy' && face !== 'dizzy') {
      closed(L);
      closed(R);
    } else if (face === 'happy') {
      arcUp(L);
      arcUp(R);
    } else if (face === 'smug') {
      // half-lidded eyes
      for (const x of [L, R]) {
        g.beginPath();
        g.ellipse(x, Y + 8, 34, 16, 0, 0, Math.PI);
        g.fill();
        g.beginPath();
        g.moveTo(x - 40, Y + 6);
        g.lineTo(x + 40, Y + 2);
        g.stroke();
      }
      g.beginPath();
      g.moveTo(R - 50, Y - 70);
      g.quadraticCurveTo(R, Y - 92, R + 46, Y - 66);
      g.stroke();
    } else if (face === 'dizzy') {
      for (const x of [L, R]) {
        g.beginPath();
        for (let a = 0; a < Math.PI * 4; a += 0.2) {
          const r = 4 + a * 3.2;
          g.lineTo(x + Math.cos(a) * r, Y + Math.sin(a) * r);
        }
        g.lineWidth = 10;
        g.stroke();
        g.lineWidth = 16;
      }
    } else {
      dot(L, face === 'shock' ? 24 : 20, face === 'shock' ? 36 : 30);
      dot(R, face === 'shock' ? 24 : 20, face === 'shock' ? 36 : 30);
    }

    // mouth
    g.beginPath();
    if (face === 'happy' || face === 'dizzy') {
      g.moveTo(206, 318);
      g.quadraticCurveTo(256, 312, 306, 318);
      g.quadraticCurveTo(256, 380, 206, 318);
      g.fill();
    } else if (face === 'smug') {
      g.moveTo(240, 330);
      g.quadraticCurveTo(262, 350, 290, 322);
      g.stroke();
    } else if (face === 'shock') {
      g.ellipse(256, 340, 26, 34, 0, 0, Math.PI * 2);
      g.fill();
    } else {
      g.moveTo(226, 326);
      g.quadraticCurveTo(256, 352, 286, 326);
      g.stroke();
    }

    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 4;
    return t;
  }, [face, blink]);

type Props = {
  position: [number, number, number];
  rotationY?: number;
  hoodie?: string;
  cap?: string; // colour of a baseball cap, if any
  face?: Face;
  blink?: boolean;
  pose?: Pose;
  t?: number; // time in seconds, drives idle/cheer motion
  lookX?: number; // turn face sideways a little
};

export const Toon: React.FC<Props> = ({
  position,
  rotationY = 0,
  hoodie = '#4a86e8',
  cap,
  face = 'open',
  blink = false,
  pose = 'idle',
  t = 0,
  lookX = 0,
}) => {
  const faceTex = useFace(face, blink);
  const dark = useMemo(() => '#' + new THREE.Color(hoodie).multiplyScalar(0.78).getHexString(), [hoodie]);

  // arm angles: [x rotation (forward/back), z rotation (out to the side)]
  const bounce = pose === 'cheer' ? Math.abs(Math.sin(t * 7)) * 0.08 : Math.sin(t * 2) * 0.01;
  const pump = pose === 'cheer' ? Math.sin(t * 7) * 0.25 : 0;
  const arms: Record<Pose, [[number, number], [number, number]]> = {
    idle: [[0.05, 0.12], [0.05, -0.12]],
    cheer: [[-2.7 + pump, 0.25], [-0.9, -0.5]],
    fists: [[-1.3 + pump, 0.55], [-1.3 - pump, -0.55]],
    wave: [[0.05, 0.12], [-2.5, -0.6 + Math.sin(t * 9) * 0.3]],
  };
  const [aL, aR] = arms[pose];

  const Arm = ({ side, a }: { side: 1 | -1; a: [number, number] }) => (
    <group position={[0.3 * side, 1.3, 0]} rotation={[a[0], 0, a[1]]}>
      <mesh position={[0, -0.24, 0]}>
        <capsuleGeometry args={[0.09, 0.32, 6, 14]} />
        <Mat color={hoodie} />
        <Outlines thickness={OUT} color={LINE} />
      </mesh>
      <mesh position={[0, -0.5, 0]}>
        <sphereGeometry args={[0.105, 20, 16]} />
        <Mat color={BODY} />
        <Outlines thickness={OUT} color={LINE} />
      </mesh>
    </group>
  );

  return (
    <group position={[position[0], position[1] + bounce, position[2]]} rotation={[0, rotationY, 0]}>
      {/* stick legs */}
      {[-0.1, 0.1].map((x) => (
        <mesh key={x} position={[x, 0.38, 0]}>
          <cylinderGeometry args={[0.045, 0.045, 0.76, 10]} />
          <Mat color={BODY} />
          <Outlines thickness={OUT} color={LINE} />
        </mesh>
      ))}
      {/* hoodie torso */}
      <mesh position={[0, 1.02, 0]} scale={[1, 1, 0.78]}>
        <capsuleGeometry args={[0.27, 0.34, 8, 20]} />
        <Mat color={hoodie} />
        <Outlines thickness={OUT} color={LINE} />
      </mesh>
      {/* hood collar */}
      <mesh position={[0, 1.38, -0.03]} rotation={[Math.PI / 2 + 0.25, 0, 0]}>
        <torusGeometry args={[0.15, 0.075, 12, 24]} />
        <Mat color={hoodie} />
        <Outlines thickness={OUT} color={LINE} />
      </mesh>
      <mesh position={[0, 1.36, -0.14]} scale={[1, 0.8, 0.7]}>
        <sphereGeometry args={[0.2, 16, 12]} />
        <Mat color={dark} />
      </mesh>
      {/* drawstrings + pocket */}
      {[-0.055, 0.055].map((x) => (
        <mesh key={x} position={[x, 1.17, 0.205]}>
          <boxGeometry args={[0.022, 0.16, 0.01]} />
          <meshBasicMaterial color="#f4f0fa" />
        </mesh>
      ))}
      <mesh position={[0, 0.86, 0.2]} rotation={[-0.12, 0, 0]}>
        <boxGeometry args={[0.28, 0.11, 0.02]} />
        <Mat color={dark} />
      </mesh>
      <Arm side={-1} a={aL} />
      <Arm side={1} a={aR} />
      {/* stick neck */}
      <mesh position={[0, 1.5, 0]}>
        <cylinderGeometry args={[0.035, 0.035, 0.26, 10]} />
        <Mat color={BODY} />
        <Outlines thickness={OUT * 0.8} color={LINE} />
      </mesh>
      {/* head */}
      <group position={[0, 2.02, 0]} rotation={[0, lookX, 0]}>
        <mesh>
          <sphereGeometry args={[0.5, 64, 48]} />
          <Mat color={BODY} rough={0.42} />
          <Outlines thickness={OUT} color={LINE} />
          <Decal position={[0, -0.02, 0.45]} rotation={[0, 0, 0]} scale={[0.62, 0.62, 0.6]} map={faceTex} />
        </mesh>
        {cap && (
          <group rotation={[-0.25, 0.4, 0]}>
            <mesh position={[0, 0.12, 0]}>
              <sphereGeometry args={[0.51, 40, 20, 0, Math.PI * 2, 0, 1.0]} />
              <Mat color={cap} />
              <Outlines thickness={OUT} color={LINE} />
            </mesh>
            <mesh position={[0, 0.38, 0.36]} rotation={[0.25, 0, 0]} scale={[1, 0.12, 1]}>
              <cylinderGeometry args={[0.22, 0.22, 0.2, 24, 1, false, -Math.PI / 2, Math.PI]} />
              <Mat color={cap} />
            </mesh>
          </group>
        )}
      </group>
    </group>
  );
};
