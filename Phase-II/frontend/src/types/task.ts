export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  user_id: string;
  created_at: string;
  updated_at: string;
}