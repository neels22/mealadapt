import { ScanResult } from '@/lib/types';
import { CheckCircle2, AlertTriangle, XCircle, ShieldCheck, ShieldAlert } from 'lucide-react';

interface Props {
  result: ScanResult;
}

const SAFETY_CONFIG = {
  safe: {
    icon: CheckCircle2,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    label: 'Safe for Family'
  },
  caution: {
    icon: AlertTriangle,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    label: 'Use with Caution'
  },
  unsafe: {
    icon: XCircle,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    label: 'Not Recommended'
  }
};

const SEVERITY_COLORS = {
  low: 'bg-yellow-100 text-yellow-800',
  medium: 'bg-orange-100 text-orange-800',
  high: 'bg-red-100 text-red-800'
};

export default function ScanResultDisplay({ result }: Props) {
  const safetyConfig = SAFETY_CONFIG[result.overall_safety as keyof typeof SAFETY_CONFIG] || SAFETY_CONFIG.caution;
  const SafetyIcon = safetyConfig.icon;

  return (
    <div className="card space-y-6">
      {/* Product Name & Overall Safety */}
      <div className={`p-4 rounded-xl border ${safetyConfig.bgColor} ${safetyConfig.borderColor}`}>
        <div className="flex items-center gap-3">
          <SafetyIcon className={`w-8 h-8 ${safetyConfig.color}`} />
          <div>
            <h2 className="text-xl font-bold">{result.product_name}</h2>
            <p className={`font-medium ${safetyConfig.color}`}>{safetyConfig.label}</p>
          </div>
        </div>
      </div>

      {/* Extracted Ingredients */}
      <div>
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <span>📋</span> Detected Ingredients
        </h3>
        <div className="flex flex-wrap gap-2">
          {result.extracted_ingredients.map((ingredient, i) => (
            <span
              key={i}
              className={`px-3 py-1 rounded-full text-sm ${
                result.safe_for_all.includes(ingredient)
                  ? 'bg-green-100 text-green-800'
                  : result.concerns.some(c => c.ingredient.toLowerCase() === ingredient.toLowerCase())
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {ingredient}
            </span>
          ))}
        </div>
      </div>

      {/* Concerns */}
      {result.concerns.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-500" />
            Concerns for Your Family
          </h3>
          <div className="space-y-3">
            {result.concerns.map((concern, i) => (
              <div key={i} className="bg-red-50 border border-red-200 rounded-xl p-4">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="font-semibold text-red-800">{concern.ingredient}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${SEVERITY_COLORS[concern.severity]}`}>
                    {concern.severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-red-700 mb-2">{concern.reason}</p>
                <div className="flex flex-wrap gap-1">
                  {concern.affected_members.map((member, j) => (
                    <span key={j} className="text-xs bg-red-200 text-red-800 px-2 py-1 rounded-full">
                      {member}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Safe Ingredients */}
      {result.safe_for_all.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-green-500" />
            Safe for Everyone
          </h3>
          <div className="flex flex-wrap gap-2">
            {result.safe_for_all.map((ingredient, i) => (
              <span key={i} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                ✓ {ingredient}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {result.recommendations.length > 0 && (
        <div className="bg-[var(--accent-blue)]/30 p-4 rounded-xl">
          <h3 className="font-semibold mb-2">💡 Recommendations</h3>
          <ul className="text-sm space-y-1">
            {result.recommendations.map((rec, i) => (
              <li key={i}>• {rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
