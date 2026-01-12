'use client';

import { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { FamilyMember, Role, ConditionType, HealthCondition } from '@/lib/types';

interface Props {
  onClose: () => void;
  onAdd: (member: FamilyMember) => void;
}

const AVATARS = ['😊', '👨', '👩', '👴', '👵', '👦', '👧', '👶', '🧑', '👱'];

export default function AddMemberModal({ onClose, onAdd }: Props) {
  const [name, setName] = useState('');
  const [avatar, setAvatar] = useState('😊');
  const [role, setRole] = useState<Role>(Role.ADULT);
  const [selectedConditions, setSelectedConditions] = useState<ConditionType[]>([]);
  const [customConditions, setCustomConditions] = useState<string[]>([]);
  const [newCustomCondition, setNewCustomCondition] = useState('');

  const toggleCondition = (condition: ConditionType) => {
    setSelectedConditions(prev =>
      prev.includes(condition)
        ? prev.filter(c => c !== condition)
        : [...prev, condition]
    );
  };

  const addCustomCondition = () => {
    const trimmed = newCustomCondition.trim();
    if (trimmed && !customConditions.includes(trimmed)) {
      setCustomConditions(prev => [...prev, trimmed]);
      setNewCustomCondition('');
    }
  };

  const removeCustomCondition = (condition: string) => {
    setCustomConditions(prev => prev.filter(c => c !== condition));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addCustomCondition();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const conditions: HealthCondition[] = selectedConditions.map(type => ({
      type,
      enabled: true,
    }));

    const member: FamilyMember = {
      id: crypto.randomUUID(),
      name: name.trim(),
      avatar,
      role,
      conditions,
      custom_restrictions: customConditions,
    };

    onAdd(member);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b border-[var(--border-light)]">
          <h2 className="text-xl font-semibold">Add Family Member</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-[var(--background)] rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Name Input */}
          <div>
            <label className="block text-sm font-medium mb-2">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter name"
              className="w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)]"
              required
            />
          </div>

          {/* Avatar Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Avatar</label>
            <div className="flex gap-2 flex-wrap">
              {AVATARS.map((emoji) => (
                <button
                  key={emoji}
                  type="button"
                  onClick={() => setAvatar(emoji)}
                  className={`text-2xl p-2 rounded-lg transition-colors ${
                    avatar === emoji
                      ? 'bg-[var(--accent-green)]'
                      : 'bg-[var(--background)] hover:bg-[var(--border-light)]'
                  }`}
                >
                  {emoji}
                </button>
              ))}
            </div>
          </div>

          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Role</label>
            <div className="flex gap-2">
              {Object.values(Role).map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setRole(r)}
                  className={`flex-1 py-2 px-3 rounded-full text-sm font-medium transition-colors ${
                    role === r
                      ? 'bg-[var(--accent-pink)] text-[var(--text-primary)]'
                      : 'bg-[var(--background)] text-[var(--text-secondary)] hover:bg-[var(--border-light)]'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          {/* Conditions Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Health Conditions (optional)
            </label>
            <div className="space-y-2">
              {Object.values(ConditionType).map((condition) => (
                <label
                  key={condition}
                  className="flex items-center gap-3 p-3 bg-[var(--background)] rounded-lg cursor-pointer hover:bg-[var(--border-light)] transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={selectedConditions.includes(condition)}
                    onChange={() => toggleCondition(condition)}
                    className="w-4 h-4 rounded accent-[var(--accent-green)]"
                  />
                  <span className="text-sm">{condition}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Custom Conditions */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Custom Conditions / Allergies
            </label>
            
            {/* Added custom conditions */}
            {customConditions.length > 0 && (
              <div className="space-y-2 mb-3">
                {customConditions.map((condition) => (
                  <div
                    key={condition}
                    className="flex items-center justify-between p-3 bg-purple-50 border border-purple-200 rounded-lg"
                  >
                    <span className="text-sm text-purple-700">{condition}</span>
                    <button
                      type="button"
                      onClick={() => removeCustomCondition(condition)}
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
                placeholder="e.g., Shellfish allergy, Low FODMAP..."
                className="flex-1 p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)] text-sm"
              />
              <button
                type="button"
                onClick={addCustomCondition}
                disabled={!newCustomCondition.trim()}
                className="px-4 py-2 bg-[var(--accent-green)] text-[var(--text-primary)] rounded-xl hover:bg-[var(--accent-green-dark)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
              >
                <Plus className="w-4 h-4" />
                Add
              </button>
            </div>
            <p className="text-xs text-[var(--text-secondary)] mt-2">
              Add any custom dietary restrictions, allergies, or conditions not listed above
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!name.trim()}
            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Add Member
          </button>
        </form>
      </div>
    </div>
  );
}
