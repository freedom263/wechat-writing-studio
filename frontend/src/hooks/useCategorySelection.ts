import { useState, useEffect } from 'react';
import { Category, Template } from '../types';
import { getCategories } from '../api/client';

export function useCategorySelection() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string>('tcm_health');
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);

  useEffect(() => {
    getCategories()
      .then((data) => {
        setCategories(data);
        if (data.length > 0) {
          const tcm = data.find((c) => c.id === 'tcm_health') || data[0];
          setSelectedCategoryId(tcm.id);
          if (tcm.templates.length > 0) {
            setSelectedTemplate(tcm.templates[0]);
          }
        }
      })
      .catch((err) => {
        console.error('加载赛道失败:', err);
      });
  }, []);

  const selectCategory = (catId: string) => {
    setSelectedCategoryId(catId);
    const cat = categories.find((c) => c.id === catId);
    if (cat && cat.templates.length > 0) {
      setSelectedTemplate(cat.templates[0]);
    } else {
      setSelectedTemplate(null);
    }
  };

  const currentCategory = categories.find((c) => c.id === selectedCategoryId);

  return {
    categories,
    selectedCategoryId,
    selectedTemplate,
    currentCategory,
    selectCategory,
    setSelectedTemplate
  };
}
