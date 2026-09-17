import React from 'react';

const TrendChart = ({ data }) => {
  // Format dates for x-axis
  const dates = data?.dates || [];
  const baseTrend = data?.base_trend || [];
  const optimistic = data?.optimistic || [];
  const pessimistic = data?.pessimistic || [];

  // Canvas height and width
  const canvasHeight = 300;
  const canvasWidth = 600;
  
  // Padding
  const padding = 40;
  
  // Find max value for scaling
  const maxValue = Math.max(
    ...baseTrend,
    ...optimistic,
    ...pessimistic
  );

  // Scale factors
  const xScale = (canvasWidth - 2 * padding) / (dates.length - 1);
  const yScale = (canvasHeight - 2 * padding) / maxValue;

  // Create points arrays
  const basePoints = dates.map((_, i) => ({
    x: padding + i * xScale,
    y: canvasHeight - (padding + baseTrend[i] * yScale)
  }));

  const optimisticPoints = dates.map((_, i) => ({
    x: padding + i * xScale,
    y: canvasHeight - (padding + optimistic[i] * yScale)
  }));

  const pessimisticPoints = dates.map((_, i) => ({
    x: padding + i * xScale,
    y: canvasHeight - (padding + pessimistic[i] * yScale)
  }));

  // Create SVG path strings
  const createPath = (points) => {
    return points.map((point, i) => 
      (i === 0 ? 'M' : 'L') + point.x + ',' + point.y
    ).join(' ');
  };

  return (
    <div className="w-full overflow-x-auto">
      <svg 
        width={canvasWidth} 
        height={canvasHeight} 
        className="mx-auto"
      >
        {/* Grid lines */}
        {[...Array(5)].map((_, i) => {
          const y = padding + (i * (canvasHeight - 2 * padding) / 4);
          return (
            <g key={i}>
              <line
                x1={padding}
                y1={y}
                x2={canvasWidth - padding}
                y2={y}
                stroke="#e5e7eb"
                strokeDasharray="4"
              />
              <text
                x={padding - 10}
                y={y}
                textAnchor="end"
                alignmentBaseline="middle"
                className="text-xs fill-gray-500"
              >
                {Math.round((maxValue - (i * maxValue / 4)) * 100) / 100}
              </text>
            </g>
          );
        })}

        {/* Date labels */}
        {dates.map((date, i) => (
          <text
            key={i}
            x={padding + i * xScale}
            y={canvasHeight - padding + 20}
            textAnchor="middle"
            className="text-xs fill-gray-500"
          >
            {date.split(' ')[0]}
          </text>
        ))}

        {/* Trend lines */}
        <path
          d={createPath(pessimisticPoints)}
          stroke="#f87171"
          strokeWidth="2"
          fill="none"
          strokeDasharray="4"
        />
        <path
          d={createPath(basePoints)}
          stroke="#3b82f6"
          strokeWidth="2"
          fill="none"
        />
        <path
          d={createPath(optimisticPoints)}
          stroke="#34d399"
          strokeWidth="2"
          fill="none"
          strokeDasharray="4"
        />
      </svg>

      {/* Legend */}
      <div className="flex justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-blue-500"></div>
          <span className="text-sm text-gray-600">Expected</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-green-400 border-dashed border-t-2"></div>
          <span className="text-sm text-gray-600">Optimistic</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-red-400 border-dashed border-t-2"></div>
          <span className="text-sm text-gray-600">Pessimistic</span>
        </div>
      </div>
    </div>
  );
};

export default TrendChart;
