'use client';

import { Grade } from '@/lib/api';

interface GradeDisplayProps {
  grade: Grade;
}

// Map criterion names to display names
const CRITERION_DISPLAY_NAMES: Record<string, string> = {
  business_value_articulation: 'Business Value Articulation',
  audience_adaptation: 'Audience Adaptation',
  handling_objections: 'Handling Objections',
  clarity_and_structure: 'Clarity and Structure',
  honesty_and_limitations: 'Honesty and Limitations',
  actionable_recommendation: 'Actionable Recommendation',
};

function getScoreColor(score: number, maxScore: number): string {
  const percentage = (score / maxScore) * 100;
  if (percentage >= 80) return 'text-green-600';
  if (percentage >= 60) return 'text-yellow-600';
  return 'text-red-600';
}

function getBarColor(score: number, maxScore: number): string {
  const percentage = (score / maxScore) * 100;
  if (percentage >= 80) return 'bg-green-500';
  if (percentage >= 60) return 'bg-yellow-500';
  return 'bg-red-500';
}

export function GradeDisplay({ grade }: GradeDisplayProps) {
  const scorePercentage = (grade.total_score / grade.max_score) * 100;

  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <div className="bg-white rounded-lg p-6 shadow-md">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Overall Score</h2>
          {grade.instructor_override && (
            <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full">
              Instructor Reviewed
            </span>
          )}
        </div>

        <div className="flex items-end gap-4 mb-4">
          <span className={`text-5xl font-bold ${getScoreColor(grade.total_score, grade.max_score)}`}>
            {Math.round(grade.total_score)}
          </span>
          <span className="text-2xl text-gray-400 mb-1">/ {grade.max_score}</span>
        </div>

        {/* Progress bar */}
        <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full ${getBarColor(grade.total_score, grade.max_score)} transition-all duration-500`}
            style={{ width: `${scorePercentage}%` }}
          />
        </div>

        <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
          <span>Graded by: {grade.graded_by === 'ai' ? 'AI' : 'Instructor'}</span>
          {grade.ai_confidence !== null && (
            <span>
              AI Confidence: {Math.round(grade.ai_confidence * 100)}%
            </span>
          )}
          <span>
            {new Date(grade.graded_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      {/* Strengths & Areas for Improvement */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-green-50 rounded-lg p-4">
          <h3 className="font-semibold text-green-800 mb-2">Strengths</h3>
          <ul className="space-y-2">
            {grade.strengths.map((strength, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-green-700">
                <span className="text-green-500 mt-0.5">✓</span>
                {strength}
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-orange-50 rounded-lg p-4">
          <h3 className="font-semibold text-orange-800 mb-2">Areas for Improvement</h3>
          <ul className="space-y-2">
            {grade.areas_for_improvement.map((area, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-orange-700">
                <span className="text-orange-500 mt-0.5">→</span>
                {area}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Criterion Breakdown */}
      <div className="bg-white rounded-lg p-6 shadow-md">
        <h3 className="font-bold text-lg mb-4">Rubric Breakdown</h3>

        <div className="space-y-6">
          {Object.entries(grade.criteria_scores).map(([name, criterion]) => (
            <div key={name} className="border-b pb-4 last:border-b-0 last:pb-0">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">
                  {CRITERION_DISPLAY_NAMES[name] || name}
                </h4>
                <span className={`font-bold ${getScoreColor(criterion.score, criterion.max_score)}`}>
                  {criterion.score} / {criterion.max_score}
                </span>
              </div>

              {/* Score bar */}
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-3">
                <div
                  className={`h-full ${getBarColor(criterion.score, criterion.max_score)}`}
                  style={{ width: `${(criterion.score / criterion.max_score) * 100}%` }}
                />
              </div>

              {/* Evidence */}
              {criterion.evidence && (
                <div className="bg-gray-50 rounded p-3 mb-2">
                  <p className="text-xs font-medium text-gray-500 mb-1">Evidence</p>
                  <p className="text-sm text-gray-700 italic">"{criterion.evidence}"</p>
                </div>
              )}

              {/* Feedback */}
              {criterion.feedback && (
                <p className="text-sm text-gray-600">{criterion.feedback}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Overall Feedback */}
      <div className="bg-white rounded-lg p-6 shadow-md">
        <h3 className="font-bold text-lg mb-4">Overall Feedback</h3>
        <div className="prose prose-sm max-w-none">
          {grade.overall_feedback.split('\n\n').map((paragraph, i) => (
            <p key={i} className="text-gray-700 mb-3">{paragraph}</p>
          ))}
        </div>
      </div>

      {/* Override reason if applicable */}
      {grade.instructor_override && grade.override_reason && (
        <div className="bg-purple-50 rounded-lg p-4">
          <h4 className="font-medium text-purple-800 mb-1">Instructor Notes</h4>
          <p className="text-sm text-purple-700">{grade.override_reason}</p>
        </div>
      )}
    </div>
  );
}
