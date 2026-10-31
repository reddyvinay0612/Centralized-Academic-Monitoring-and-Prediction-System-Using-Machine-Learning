import { RISK_THRESHOLDS } from './constants';

/**
 * Determine risk level category based on 0-1 probability score
 * Rules:
 *   Low: score < 0.35
 *   Medium: 0.35 <= score < 0.60
 *   High: score >= 0.60
 */
export function getRiskLevel(score) {
  if (score == null || isNaN(score)) return 'low';
  if (score < RISK_THRESHOLDS.LOW_MAX) return 'low';
  if (score < RISK_THRESHOLDS.MEDIUM_MAX) return 'medium';
  return 'high';
}

/**
 * Returns exact design system hex color for a risk level
 */
export function getRiskColor(level) {
  switch (level?.toLowerCase()) {
    case 'high':
      return '#d9445a';
    case 'medium':
      return '#d89a06';
    case 'low':
      return '#0f9d8a';
    default:
      return '#5b6b82';
  }
}

/**
 * Human-readable risk label
 */
export function getRiskLabel(level) {
  switch (level?.toLowerCase()) {
    case 'high':
      return 'High risk';
    case 'medium':
      return 'Medium risk';
    case 'low':
      return 'Low risk';
    default:
      return 'Unknown';
  }
}

/**
 * Tailwind badge styling ensuring color is NEVER the only signal (accessible contrast)
 */
export function getRiskBadgeClasses(level) {
  switch (level?.toLowerCase()) {
    case 'high':
      return 'bg-risk-high/10 text-risk-high border border-risk-high/30 dark:bg-risk-high/20 dark:border-risk-high/40';
    case 'medium':
      return 'bg-risk-medium/10 text-risk-medium border border-risk-medium/30 dark:bg-risk-medium/20 dark:border-risk-medium/40';
    case 'low':
      return 'bg-risk-low/10 text-risk-low border border-risk-low/30 dark:bg-risk-low/20 dark:border-risk-low/40';
    default:
      return 'bg-gray-100 text-gray-700 border border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700';
  }
}

/**
 * Formats 0-1 float to integer percentage
 */
export function formatRiskScore(score) {
  if (score == null || isNaN(score)) return '0%';
  return `${Math.round(score * 100)}%`;
}
