import React from 'react';
import { Category } from '../types';
import { 
  HeartPulse, 
  BookOpen, 
  Flame, 
  Briefcase, 
  Heart, 
  Cpu, 
  Coffee, 
  GraduationCap, 
  Landmark, 
  Compass, 
  TrendingUp 
} from 'lucide-react';

interface TrackBarProps {
  categories: Category[];
  selectedCategoryId: string;
  onSelectCategory: (id: string) => void;
}

const ICON_MAP: Record<string, React.ReactNode> = {
  HeartPulse: <HeartPulse className="w-4 h-4" />,
  BookOpen: <BookOpen className="w-4 h-4" />,
  Flame: <Flame className="w-4 h-4" />,
  Briefcase: <Briefcase className="w-4 h-4" />,
  Heart: <Heart className="w-4 h-4" />,
  Cpu: <Cpu className="w-4 h-4" />,
  Coffee: <Coffee className="w-4 h-4" />,
  GraduationCap: <GraduationCap className="w-4 h-4" />,
  Landmark: <Landmark className="w-4 h-4" />,
  Compass: <Compass className="w-4 h-4" />,
  TrendingUp: <TrendingUp className="w-4 h-4" />
};

export const TrackBar: React.FC<TrackBarProps> = ({
  categories,
  selectedCategoryId,
  onSelectCategory
}) => {
  return (
    <div className="bg-white border-b border-slate-200 px-6 py-2.5">
      <div className="flex items-center space-x-2 overflow-x-auto pb-0.5 scrollbar-none">
        {categories.map((cat) => {
          const isSelected = cat.id === selectedCategoryId;
          return (
            <button
              key={cat.id}
              onClick={() => onSelectCategory(cat.id)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-smooth ${
                isSelected
                  ? 'bg-slate-900 text-white shadow-lg scale-105'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200 hover:text-slate-900 border border-slate-200 hover:scale-102'
              }`}
            >
              <span>{ICON_MAP[cat.icon] || <BookOpen className="w-3.5 h-3.5" />}</span>
              <span>{cat.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
