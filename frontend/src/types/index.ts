export interface Template {
  id: string;
  category_id: string;
  name: string;
  description: string;
  tag: string;
  sort_order: number;
}

export interface Category {
  id: string;
  name: string;
  icon: string;
  description?: string;
  sort_order: number;
  templates: Template[];
}

export interface OutlineCandidate {
  id?: string;
  index: number;
  title: string;
  summary: string;
  tags: string[];
  outline_sections: string[];
}

export interface PromptConfig {
  id: string;
  template_id: string;
  prompt_type: 'outline' | 'article';
  system_prompt: string;
  user_prompt_template: string;
  model_name: string;
  temperature: number;
  version: number;
  is_active: boolean;
  append_disclaimer: boolean;
  disclaimer_text?: string;
}

export interface Article {
  id: string;
  category_id?: string;
  template_id?: string;
  input_type: string;
  raw_input?: string;
  input_options?: Record<string, any>;
  selected_title?: string;
  outline_content?: string;
  final_content?: string;
  status: string;
  word_count: number;
  disclaimer?: string;
  created_at?: string;
  candidates?: OutlineCandidate[];
}
