'use client';

import { useState } from 'react';
import { RecipeAnalysis, VerdictType } from '@/lib/types';
import { CheckCircle2, AlertTriangle, XCircle, Bookmark, Check, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

interface Props {
  analysis: RecipeAnalysis;
  recipeText?: string;
  onSaved?: () => void;
}

const VERDICT_CONFIG = {
  [VerdictType.SAFE]: {
    icon: CheckCircle2,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    label: 'Safe'
  },
  [VerdictType.NEEDS_ADAPTATION]: {
    icon: AlertTriangle,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    label: 'Needs Adaptation'
  },
  [VerdictType.NOT_RECOMMENDED]: {
    icon: XCircle,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    label: 'Not Recommended'
  }
};

export default function RecipeAnalysisDisplay({ analysis, recipeText, onSaved }: Props) {
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    if (saved || saving) return;
    
    setSaving(true);
    setError(null);
    
    try {
      await api.saveRecipe({
        dish_name: analysis.dish_name,
        recipe_text: recipeText || '',
        analysis: analysis,
        tags: [],
        notes: undefined
      });
      setSaved(true);
      onSaved?.();
    } catch (err) {
      setError('Failed to save recipe');
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to save recipe:', err);
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card space-y-6">
      {/* Header with Save Button */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h2 className="text-2xl font-bold mb-2">{analysis.dish_name}</h2>
          <p className="text-[var(--text-secondary)]">{analysis.base_description}</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving || saved}
          className={`flex items-center gap-2 px-4 py-2 rounded-full font-medium transition-all ${
            saved
              ? 'bg-green-100 text-green-700 cursor-default'
              : saving
                ? 'bg-gray-100 text-gray-400 cursor-wait'
                : 'bg-[var(--accent-green)] text-[var(--text-primary)] hover:bg-[#98C5AA]'
          }`}
          title={saved ? 'Recipe saved' : 'Save to My Recipes'}
        >
          {saving ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Saving...
            </>
          ) : saved ? (
            <>
              <Check className="w-4 h-4" />
              Saved
            </>
          ) : (
            <>
              <Bookmark className="w-4 h-4" />
              Save
            </>
          )}
        </button>
      </div>
      
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      {/* Member Verdicts */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Family Analysis</h3>
        
        {analysis.member_verdicts.map((verdict) => {
          const config = VERDICT_CONFIG[verdict.verdict];
          const Icon = config.icon;

          return (
            <div 
              key={verdict.member_id} 
              className={`p-4 rounded-xl border ${config.bgColor} ${config.borderColor}`}
            >
              <div className="flex items-start gap-3">
                <Icon className={`w-6 h-6 ${config.color} flex-shrink-0 mt-1`} />
                <div className="flex-1">
                  {/* Member Name and Verdict */}
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="font-semibold">{verdict.member_name}</h4>
                    <span className={`text-sm font-medium ${config.color}`}>
                      {config.label}
                    </span>
                  </div>

                  {/* Reasons */}
                  {verdict.reasons.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm font-medium mb-1">Reasons:</p>
                      <ul className="text-sm space-y-1">
                        {verdict.reasons.map((reason, i) => (
                          <li key={i} className="text-[var(--text-secondary)]">• {reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Concerns */}
                  {verdict.concerns.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm font-medium mb-1">Concerns:</p>
                      <ul className="text-sm space-y-1">
                        {verdict.concerns.map((concern, i) => (
                          <li key={i} className="text-red-700">⚠️ {concern}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Adaptations */}
                  {verdict.adaptations && (
                    <div className="mt-3 p-3 bg-white rounded-lg border border-gray-100">
                      <p className="text-sm font-semibold mb-2">Recommended Adaptations:</p>
                      
                      {/* Modifications */}
                      {verdict.adaptations.modifications.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs font-medium text-[var(--text-secondary)] mb-1">
                            Modifications:
                          </p>
                          <ul className="text-sm space-y-1">
                            {verdict.adaptations.modifications.map((mod, i) => (
                              <li key={i} className="text-green-700">✓ {mod}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Substitutions */}
                      {verdict.adaptations.substitutions.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs font-medium text-[var(--text-secondary)] mb-1">
                            Substitutions:
                          </p>
                          {verdict.adaptations.substitutions.map((sub, i) => (
                            <div key={i} className="text-sm mb-2">
                              <div className="flex items-center gap-2">
                                <span className="line-through text-red-500">
                                  {sub.original}
                                </span>
                                <span className="text-[var(--text-secondary)]">→</span>
                                <span className="text-green-600 font-medium">
                                  {sub.replacement}
                                </span>
                              </div>
                              <p className="text-xs text-[var(--text-secondary)] ml-4">
                                {sub.reason}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Preparation Changes */}
                      {verdict.adaptations.preparation_changes.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-[var(--text-secondary)] mb-1">
                            Preparation Changes:
                          </p>
                          <ul className="text-sm space-y-1">
                            {verdict.adaptations.preparation_changes.map((change, i) => (
                              <li key={i} className="text-blue-700">🔧 {change}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Nutritional Notes */}
                  {verdict.nutritional_notes && (
                    <p className="text-sm text-[var(--text-secondary)] mt-2 italic">
                      💡 {verdict.nutritional_notes}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* General Tips */}
      {analysis.general_tips.length > 0 && (
        <div className="bg-[var(--accent-yellow)] p-4 rounded-xl">
          <h4 className="font-semibold mb-2">💡 General Tips</h4>
          <ul className="text-sm space-y-1">
            {analysis.general_tips.map((tip, i) => (
              <li key={i}>• {tip}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
