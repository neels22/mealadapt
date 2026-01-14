'use client';

import { useState } from 'react';
import MemberCard from './MemberCard';
import AddMemberModal from './AddMemberModal';
import { FamilyProfile as FamilyProfileType, FamilyMember } from '@/lib/types';
import { api } from '@/lib/api';

interface Props {
  profile: FamilyProfileType;
  onUpdate: () => void;
}

export default function FamilyProfile({ profile, onUpdate }: Props) {
  const [showAddModal, setShowAddModal] = useState(false);

  const handleAddMember = async (member: FamilyMember) => {
    try {
      await api.addMember(member);
      onUpdate();
      setShowAddModal(false);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to add member:', error);
      }
    }
  };

  const handleUpdateMember = async (member: FamilyMember) => {
    try {
      await api.updateMember(member.id, member);
      onUpdate();
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to update member:', error);
      }
    }
  };

  const handleDeleteMember = async (memberId: string) => {
    try {
      await api.deleteMember(memberId);
      onUpdate();
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to delete member:', error);
      }
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <span>👨‍👩‍👧‍👦</span> My Family
        </h2>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-[var(--accent-green)] hover:bg-[var(--accent-green-hover)] text-[var(--text-primary)] px-4 py-2 rounded-full text-sm font-medium transition-colors"
        >
          + Add
        </button>
      </div>

      {profile.members.length === 0 ? (
        <p className="text-[var(--text-secondary)] text-center py-8">
          No family members yet. Add your first family member to get started!
        </p>
      ) : (
        <div className="space-y-3">
          {profile.members.map((member) => (
            <MemberCard
              key={member.id}
              member={member}
              onUpdate={handleUpdateMember}
              onDelete={handleDeleteMember}
            />
          ))}
        </div>
      )}

      {showAddModal && (
        <AddMemberModal
          onClose={() => setShowAddModal(false)}
          onAdd={handleAddMember}
        />
      )}
    </div>
  );
}
