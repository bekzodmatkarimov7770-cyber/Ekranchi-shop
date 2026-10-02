import React from 'react';
import { Composition } from 'remotion';
import { Promo } from './Promo';
import { FPS, DURATION } from './timeline';
export const RemotionRoot: React.FC = () => (
  <Composition id="Promo" component={Promo} durationInFrames={Math.round(DURATION * FPS)} fps={FPS} width={1080} height={1920} />
);
