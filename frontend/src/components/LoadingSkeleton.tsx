import React from 'react';

interface LoadingSkeletonProps {
  type?: 'template' | 'candidate' | 'article';
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ type = 'template' }) => {
  if (type === 'template') {
    return (
      <div className="grid grid-cols-2 gap-2.5">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="p-3 rounded-xl border border-slate-200 bg-white animate-pulse">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="skeleton-title"></div>
                <div className="skeleton w-12 h-4"></div>
              </div>
              <div className="skeleton-text"></div>
              <div className="skeleton-text w-3/4"></div>
              <div className="mt-3 pt-2 border-t border-slate-100 flex justify-between items-center">
                <div className="skeleton w-16 h-3"></div>
                <div className="skeleton w-20 h-3"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (type === 'candidate') {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="rounded-xl border border-slate-200 bg-slate-50/40 p-4 animate-pulse">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="skeleton w-12 h-5"></div>
                <div className="skeleton w-4 h-4 rounded-full"></div>
              </div>
              <div className="skeleton-title"></div>
              <div className="skeleton-text"></div>
              <div className="skeleton-text w-5/6"></div>
              <div className="flex gap-1">
                <div className="skeleton w-16 h-5"></div>
                <div className="skeleton w-20 h-5"></div>
              </div>
              <div className="bg-white p-2.5 rounded-lg border border-slate-200 space-y-1">
                <div className="skeleton-text w-full"></div>
                <div className="skeleton-text w-full"></div>
                <div className="skeleton-text w-2/3"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (type === 'article') {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-5 animate-pulse">
        <div className="space-y-4">
          <div className="skeleton-title w-1/2"></div>
          <div className="space-y-2">
            <div className="skeleton-text"></div>
            <div className="skeleton-text"></div>
            <div className="skeleton-text w-4/5"></div>
          </div>
          <div className="space-y-2">
            <div className="skeleton-text"></div>
            <div className="skeleton-text"></div>
            <div className="skeleton-text w-3/4"></div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};
