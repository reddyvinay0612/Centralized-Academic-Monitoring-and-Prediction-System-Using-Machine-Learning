import { describe, it, expect } from 'vitest';
import { getRiskLevel, getRiskColor, formatRiskScore } from '../src/utils/risk';

describe('Risk Utilities', () => {
  it('correctly categorizes risk scores into tiers', () => {
    expect(getRiskLevel(0.15)).toBe('low');
    expect(getRiskLevel(0.34)).toBe('low');
    expect(getRiskLevel(0.35)).toBe('medium');
    expect(getRiskLevel(0.59)).toBe('medium');
    expect(getRiskLevel(0.60)).toBe('high');
    expect(getRiskLevel(0.92)).toBe('high');
  });

  it('maps correct design tokens for risk colors', () => {
    expect(getRiskColor('low')).toBe('#0f9d8a');
    expect(getRiskColor('medium')).toBe('#d89a06');
    expect(getRiskColor('high')).toBe('#d9445a');
  });

  it('formats probability scores into clean percentage labels', () => {
    expect(formatRiskScore(0.854)).toBe('85%');
    expect(formatRiskScore(0.12)).toBe('12%');
    expect(formatRiskScore(0)).toBe('0%');
  });
});
