'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, Plus, Trash2, X } from 'lucide-react';
import { FamilyMember, ConditionType, Role, HealthCondition } from '@/lib/types';

interface Props {
  member: FamilyMember;
  onUpdate: (member: FamilyMember) => void;
  onDelete: (memberId: string) => void;
}

const CONDITION_BADGES: Record<ConditionType, string> = {
  [ConditionType.DIABETES]: 'badge-diabetes',
  [ConditionType.HYPERTENSION]: 'badge-hypertension',
  [ConditionType.HIGH_URIC_ACID]: 'badge-uric',
  [ConditionType.PEANUT_ALLERGY]: 'badge-allergy',
  [ConditionType.HEART_DISEASE]: 'badge-heart',
  [ConditionType.KIDNEY_DISEASE]: 'badge-kidney',
  [ConditionType.CELIAC]: 'badge-celiac',
  [ConditionType.LACTOSE_INTOLERANCE]: 'badge-lactose',
};

const ROLE_EMOJI: Record<Role, string> = {
  [Role.ADULT]: '🧑',
  [Role.CHILD]: '👦',
  [Role.BABY]: '👶',
};

export default function MemberCard({ member, onUpdate, onDelete }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [newCustomCondition, setNewCustomCondition] = useState('');

  const activeConditions = member.conditions.filter(c => c.enabled);
  const customConditions = member.custom_restrictions || [];

  const toggleCondition = (conditionType: ConditionType) => {
    const existingCondition = member.conditions.find(c => c.type === conditionType);
    
    let updatedConditions: HealthCondition[];
    if (existingCondition) {
      updatedConditions = member.conditions.map(c =>
        c.type === conditionType ? { ...c, enabled: !c.enabled } : c
      );
    } else {
      updatedConditions = [...member.conditions, { type: conditionType, enabled: true }];
    }

    onUpdate({
      ...member,
      conditions: updatedConditions
    });
  };

  const isConditionEnabled = (conditionType: ConditionType): boolean => {
    const condition = member.conditions.find(c => c.type === conditionType);
    return condition?.enabled || false;
  };

  const addCustomCondition = () => {
    const trimmed = newCustomCondition.trim();
    if (trimmed && !customConditions.includes(trimmed)) {
      onUpdate({
        ...member,
        custom_restrictions: [...customConditions, trimmed]
      });
      setNewCustomCondition('');
    }
  };

  const removeCustomCondition = (condition: string) => {
    onUpdate({
      ...member,
      custom_restrictions: customConditions.filter(c => c !== condition)
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      e.stopPropagation();
      addCustomCondition();
    }
  };

  return (
    <div className="bg-[var(--background)] rounded-xl p-4">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <div className="text-3xl">{member.avatar}</div>
          <div>
            <h3 className="font-semibold">{member.name}</h3>
            <div className="flex gap-2 flex-wrap mt-1">
              {member.role === Role.BABY && (
                <span className="badge badge-baby">Baby</span>
              )}
              {activeConditions.map(c => (
                <span
                  key={c.type}
                  className={`badge ${CONDITION_BADGES[c.type]}`}
                >
                  {c.type}
                </span>
              ))}
              {customConditions.map(c => (
                <span
                  key={c}
                  className="badge bg-purple-100 text-purple-700 border-purple-200"
                >
                  {c}
                </span>
              ))}
            </div>
          </div>
        </div>
        {expanded ? (
          <ChevronUp className="w-5 h-5 text-[var(--text-secondary)]" />
        ) : (
          <ChevronDown className="w-5 h-5 text-[var(--text-secondary)]" />
        )}
      </div>

      {expanded && (
        <div className="mt-4 space-y-4 border-t border-[var(--border-light)] pt-4">
          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Role</label>
            <div className="flex gap-2">
              {Object.values(Role).map(role => (
                <button
                  key={role}
                  onClick={(e) => {
                    e.stopPropagation();
                    onUpdate({ ...member, role });
                  }}
                  className={`px-4 py-2 rounded-full text-sm transition-colors ${
                    member.role === role
                      ? 'bg-[var(--accent-pink)] text-[var(--text-primary)]'
                      : 'bg-white text-[var(--text-secondary)] hover:bg-[var(--background)]'
                  }`}
                >
                  {ROLE_EMOJI[role]} {role}
                </button>
              ))}
            </div>
          </div>

          {/* Conditions */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Health Conditions
            </label>
            <div className="space-y-2">
              {Object.values(ConditionType).map(conditionType => {
                const enabled = isConditionEnabled(conditionType);

                return (
                  <div
                    key={conditionType}
                    className="flex items-center justify-between p-3 bg-white rounded-lg"
                  >
                    <span className="text-sm">{conditionType}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleCondition(conditionType);
                      }}
                      className={`toggle ${enabled ? 'toggle-on' : 'toggle-off'}`}
                    >
                      <div className="toggle-knob" />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Custom Conditions */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Custom Conditions / Allergies
            </label>
            
            {/* List of custom conditions */}
            {customConditions.length > 0 && (
              <div className="space-y-2 mb-3">
                {customConditions.map((condition) => (
                  <div
                    key={condition}
                    className="flex items-center justify-between p-3 bg-purple-50 border border-purple-200 rounded-lg"
                  >
                    <span className="text-sm text-purple-700">{condition}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        removeCustomCondition(condition);
                      }}
                      className="p-1 hover:bg-purple-100 rounded-full text-purple-400 hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Add new custom condition */}
            <div className="flex gap-2">
              <input
                type="text"
                value={newCustomCondition}
                onChange={(e) => setNewCustomCondition(e.target.value)}
                onKeyDown={handleKeyDown}
                onClick={(e) => e.stopPropagation()}
                placeholder="Add custom condition..."
                className="flex-1 p-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)] text-sm"
              />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  addCustomCondition();
                }}
                disabled={!newCustomCondition.trim()}
                className="px-3 py-2 bg-[var(--accent-green)] text-[var(--text-primary)] rounded-lg hover:bg-[var(--accent-green-dark)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 text-sm"
              >
                <Plus className="w-4 h-4" />
                Add
              </button>
            </div>
          </div>

          {/* Delete Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (confirm(`Remove ${member.name} from family?`)) {
                onDelete(member.id);
              }
            }}
            className="w-full bg-[var(--accent-red)] hover:bg-[var(--accent-red-hover)] text-[#8A2A2A] py-2 rounded-full font-medium transition-colors"
          >
            Remove {member.name}
          </button>
        </div>
      )}
    </div>
  );
}
