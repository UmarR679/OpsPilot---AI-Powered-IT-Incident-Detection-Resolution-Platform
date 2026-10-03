import React from 'react';

export default function SeverityBadge({ severity }) {
  const sevLower = (severity || 'low').toLowerCase();
  let badgeClass = 'badge-low';
  
  if (sevLower === 'critical') badgeClass = 'badge-critical';
  else if (sevLower === 'high') badgeClass = 'badge-high';
  else if (sevLower === 'medium') badgeClass = 'badge-medium';

  return (
    <span className={`badge ${badgeClass}`}>
      {severity || 'Low'}
    </span>
  );
}
