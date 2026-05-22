'use client';

import { useState } from 'react';
import { FeedbackAssessments } from '@/lib/types';

interface MicroFeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (assessments: FeedbackAssessments) => void;
}

const sliderConfig = [
  { key: 'lower_back_stiffness' as const, label: 'Lower Back', icon: '🦴' },
  { key: 'shoulder_tension' as const, label: 'Shoulders', icon: '💪' },
  { key: 'neck_pain' as const, label: 'Neck', icon: '🦒' },
  { key: 'eye_strain' as const, label: 'Eye Strain', icon: '👁️' },
  { key: 'mental_fatigue' as const, label: 'Mental Fatigue', icon: '🧠' },
];

function getValueClass(v: number) {
  if (v <= 2) return 'low';
  if (v <= 3) return 'mid';
  return 'high';
}

const labels = ['', 'Fine', 'Mild', 'Moderate', 'Sore', 'Severe'];

export default function MicroFeedbackModal({ isOpen, onClose, onSubmit }: MicroFeedbackModalProps) {
  const [values, setValues] = useState<FeedbackAssessments>({
    lower_back_stiffness: 1,
    shoulder_tension: 1,
    neck_pain: 1,
    eye_strain: 1,
    mental_fatigue: 1,
  });

  if (!isOpen) return null;

  const handleChange = (key: keyof FeedbackAssessments, val: number) => {
    setValues((prev) => ({ ...prev, [key]: val }));
  };

  const handleSubmit = () => {
    onSubmit(values);
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <h2 className="modal-title">🩺 Quick Health Check-In</h2>
        <p className="modal-subtitle">Rate how you&apos;re feeling right now. Takes 10 seconds.</p>

        <div className="slider-group">
          {sliderConfig.map(({ key, label, icon }) => (
            <div key={key} className="slider-item">
              <div className="slider-label">
                <span className="slider-name">{icon} {label}</span>
                <span className={`slider-value ${getValueClass(values[key])}`}>
                  {values[key]} — {labels[values[key]]}
                </span>
              </div>
              <input
                type="range"
                min={1}
                max={5}
                value={values[key]}
                onChange={(e) => handleChange(key, parseInt(e.target.value))}
              />
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSubmit}>
            Submit Check-In
          </button>
        </div>
      </div>
    </div>
  );
}
