'use client';

import { useState } from 'react';
import { Heart, Trash2, ChevronDown, ChevronUp, Tag, AlertTriangle, Check, RefreshCw } from 'lucide-react';
import { SavedRecipe, VerdictType, MemberVerdict } from '@/lib/types';

interface Props {
  recipe: SavedRecipe;
  onToggleFavorite: (id: string, isFavorite: boolean) => void;
  onDelete: (id: string) => void;
  onClick?: (recipe: SavedRecipe) => void;
}

const SAFETY_COLORS = {
  safe: 'bg-green-100 text-green-700 border-green-200',
  caution: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  unsafe: 'bg-red-100 text-red-700 border-red-200',
};

// Member Verdict Card with expandable details
function MemberVerdictCard({ verdict }: { verdict: MemberVerdict }) {
  const [showDetails, setShowDetails] = useState(false);
  
  const verdictConfig = {
    [VerdictType.SAFE]: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-700',
      icon: <Check className="w-4 h-4" />,
      label: 'Safe'
    },
    [VerdictType.NEEDS_ADAPTATION]: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200', 
      text: 'text-yellow-700',
      icon: <RefreshCw className="w-4 h-4" />,
      label: 'Needs Adaptation'
    },
    [VerdictType.NOT_RECOMMENDED]: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-700',
      icon: <AlertTriangle className="w-4 h-4" />,
      label: 'Not Recommended'
    }
  };

  const config = verdictConfig[verdict.verdict] || verdictConfig[VerdictType.SAFE];
  
  const hasDetails = (verdict.reasons && verdict.reasons.length > 0) ||
                     (verdict.concerns && verdict.concerns.length > 0) ||
                     (verdict.adaptations?.modifications && verdict.adaptations.modifications.length > 0) ||
                     (verdict.adaptations?.substitutions && verdict.adaptations.substitutions.length > 0) ||
                     (verdict.adaptations?.preparation_changes && verdict.adaptations.preparation_changes.length > 0) ||
                     verdict.nutritional_notes;

  return (
    <div className={`rounded-lg border ${config.border} ${config.bg} overflow-hidden`}>
      {/* Header - always visible */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          if (hasDetails) setShowDetails(!showDetails);
        }}
        className={`w-full p-3 flex items-center justify-between ${hasDetails ? 'cursor-pointer hover:bg-black/5' : 'cursor-default'}`}
      >
        <div className="flex items-center gap-2">
          <span className={config.text}>{config.icon}</span>
          <span className={`font-medium ${config.text}`}>{verdict.member_name}</span>
          <span className={`text-sm ${config.text} opacity-75`}>— {config.label}</span>
        </div>
        {hasDetails && (
          <span className={config.text}>
            {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </span>
        )}
      </button>

      {/* Expandable details */}
      {showDetails && hasDetails && (
        <div className="px-3 pb-3 space-y-3 border-t border-inherit">
          {/* Concerns */}
          {verdict.concerns && verdict.concerns.length > 0 && (
            <div className="pt-3">
              <h5 className="text-xs font-semibold text-red-600 mb-1 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                Concerns
              </h5>
              <ul className="space-y-0.5">
                {verdict.concerns.map((concern, i) => (
                  <li key={i} className="text-sm text-red-600">• {concern}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Reasons */}
          {verdict.reasons && verdict.reasons.length > 0 && (
            <div className="pt-2">
              <h5 className="text-xs font-semibold text-gray-600 mb-1">Why</h5>
              <ul className="space-y-0.5">
                {verdict.reasons.map((reason, i) => (
                  <li key={i} className="text-sm text-gray-600">• {reason}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Adaptations */}
          {verdict.adaptations && (
            <div className="pt-2 space-y-2">
              {verdict.adaptations.modifications && verdict.adaptations.modifications.length > 0 && (
                <div>
                  <h5 className="text-xs font-semibold text-[var(--accent-green-dark)] mb-1">✨ Modifications</h5>
                  <ul className="space-y-0.5">
                    {verdict.adaptations.modifications.map((mod, i) => (
                      <li key={i} className="text-sm text-[var(--text-secondary)]">• {mod}</li>
                    ))}
                  </ul>
                </div>
              )}

              {verdict.adaptations.substitutions && verdict.adaptations.substitutions.length > 0 && (
                <div>
                  <h5 className="text-xs font-semibold text-[var(--accent-green-dark)] mb-1">🔄 Substitutions</h5>
                  <ul className="space-y-1">
                    {verdict.adaptations.substitutions.map((sub, i) => (
                      <li key={i} className="text-sm text-[var(--text-secondary)]">
                        <span className="line-through text-red-400">{sub.original}</span>
                        <span className="mx-2">→</span>
                        <span className="text-green-600 font-medium">{sub.replacement}</span>
                        {sub.reason && <span className="text-xs text-gray-400 ml-1">({sub.reason})</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {verdict.adaptations.preparation_changes && verdict.adaptations.preparation_changes.length > 0 && (
                <div>
                  <h5 className="text-xs font-semibold text-[var(--accent-green-dark)] mb-1">👨‍🍳 Preparation Changes</h5>
                  <ul className="space-y-0.5">
                    {verdict.adaptations.preparation_changes.map((change, i) => (
                      <li key={i} className="text-sm text-[var(--text-secondary)]">• {change}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Nutritional notes */}
          {verdict.nutritional_notes && (
            <div className="pt-2">
              <h5 className="text-xs font-semibold text-blue-600 mb-1">📊 Nutritional Notes</h5>
              <p className="text-sm text-blue-600">{verdict.nutritional_notes}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function SavedRecipeCard({ recipe, onToggleFavorite, onDelete, onClick }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Delete "${recipe.dish_name}" from your saved recipes?`)) {
      setIsDeleting(true);
      onDelete(recipe.id);
    }
  };

  const handleToggleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleFavorite(recipe.id, !recipe.is_favorite);
  };

  const handleExpand = (e: React.MouseEvent) => {
    e.stopPropagation();
    setExpanded(!expanded);
  };

  // Get overall safety status from analysis
  const overallSafety = recipe.analysis?.overall_safety || 'safe';
  const safetyColor = SAFETY_COLORS[overallSafety as keyof typeof SAFETY_COLORS] || SAFETY_COLORS.safe;

  // Format date
  const formattedDate = recipe.created_at 
    ? new Date(recipe.created_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    : '';

  return (
    <div 
      className={`card hover:shadow-md transition-all cursor-pointer ${isDeleting ? 'opacity-50' : ''}`}
      onClick={() => onClick?.(recipe)}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-lg truncate">{recipe.dish_name}</h3>
            {recipe.is_favorite && (
              <Heart className="w-4 h-4 fill-red-500 text-red-500 flex-shrink-0" />
            )}
          </div>
          
          {/* Safety Badge */}
          <div className="flex items-center gap-2 mb-2">
            <span className={`text-xs px-2 py-0.5 rounded-full border ${safetyColor}`}>
              {overallSafety === 'safe' ? '✓ Safe' : overallSafety === 'caution' ? '⚠ Caution' : '✗ Unsafe'}
            </span>
            {formattedDate && (
              <span className="text-xs text-[var(--text-secondary)]">{formattedDate}</span>
            )}
          </div>

          {/* Tags */}
          {recipe.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {recipe.tags.map((tag, i) => (
                <span 
                  key={i} 
                  className="text-xs bg-[var(--background)] text-[var(--text-secondary)] px-2 py-0.5 rounded-full flex items-center gap-1"
                >
                  <Tag className="w-3 h-3" />
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Description preview */}
          {recipe.analysis?.base_description && (
            <p className="text-sm text-[var(--text-secondary)] line-clamp-2">
              {recipe.analysis.base_description}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2">
          <button
            onClick={handleToggleFavorite}
            className={`p-2 rounded-full transition-colors ${
              recipe.is_favorite 
                ? 'bg-red-50 text-red-500 hover:bg-red-100' 
                : 'bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-red-400'
            }`}
            title={recipe.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Heart className={`w-5 h-5 ${recipe.is_favorite ? 'fill-current' : ''}`} />
          </button>
          <button
            onClick={handleDelete}
            className="p-2 rounded-full bg-gray-100 text-gray-400 hover:bg-red-50 hover:text-red-500 transition-colors"
            title="Delete recipe"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Expandable details */}
      <button
        onClick={handleExpand}
        className="w-full mt-3 pt-3 border-t border-gray-100 flex items-center justify-center gap-1 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
      >
        {expanded ? (
          <>
            <ChevronUp className="w-4 h-4" />
            Hide details
          </>
        ) : (
          <>
            <ChevronDown className="w-4 h-4" />
            Show analysis
          </>
        )}
      </button>

      {expanded && recipe.analysis && (
        <div className="mt-3 space-y-3">
          {/* Member verdicts with details */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Family Analysis</h4>
            {recipe.analysis.member_verdicts?.map((verdict) => (
              <MemberVerdictCard key={verdict.member_id} verdict={verdict} />
            ))}
          </div>

          {/* General Tips */}
          {recipe.analysis.general_tips && recipe.analysis.general_tips.length > 0 && (
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <h4 className="text-sm font-medium text-blue-700 mb-2">💡 General Tips</h4>
              <ul className="space-y-1">
                {recipe.analysis.general_tips.map((tip, i) => (
                  <li key={i} className="text-sm text-blue-600">• {tip}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Notes */}
          {recipe.notes && (
            <div className="bg-[var(--background)] p-3 rounded-lg">
              <h4 className="text-sm font-medium mb-1">Notes</h4>
              <p className="text-sm text-[var(--text-secondary)]">{recipe.notes}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
