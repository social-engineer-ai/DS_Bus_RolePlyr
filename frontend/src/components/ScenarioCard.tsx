'use client';

import { Scenario } from '@/lib/api';

interface ScenarioCardProps {
  scenario: Scenario;
  onSelect: (scenario: Scenario) => void;
}

export function ScenarioCard({ scenario, onSelect }: ScenarioCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-800">
            {scenario.name}
          </h3>
          <p className="mt-1 text-sm text-gray-600">
            {scenario.persona_name} - {scenario.persona_title}
          </p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            scenario.is_practice
              ? 'bg-green-100 text-green-700'
              : 'bg-orange-100 text-orange-700'
          }`}
        >
          {scenario.is_practice ? 'Practice' : 'Graded'}
        </span>
      </div>

      {scenario.description && (
        <p className="mt-3 text-sm text-gray-600">{scenario.description}</p>
      )}

      {scenario.persona_background && (
        <div className="mt-4 rounded-lg bg-gray-50 p-3">
          <p className="text-xs font-medium text-gray-500 uppercase">
            About {scenario.persona_name}
          </p>
          <p className="mt-1 text-sm text-gray-600 line-clamp-3">
            {scenario.persona_background}
          </p>
        </div>
      )}

      <div className="mt-4 flex items-center justify-between">
        <span className="text-xs text-gray-500">
          ~{scenario.max_turns} turns max
        </span>
        <button
          onClick={() => onSelect(scenario)}
          className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600"
        >
          Start Practice
        </button>
      </div>
    </div>
  );
}
