export interface TodoStats {
  total: number;
  completed: number;
  pending: number;
  completion_rate: number;
}

export interface HabitStats {
  total: number;
  active: number;
  completion_rate: number;
  average_streak: number;
}

export interface ProductivityStats {
  date: string;
  todos_completed: number;
  habits_completed: number;
}

export interface CategoryDistribution {
  [key: string]: number;
}

export interface PriorityDistribution {
  [key: string]: number;
}

export interface DashboardStats {
  todo_stats: TodoStats;
  habit_stats: HabitStats;
  productivity_trend: ProductivityStats[];
  category_distribution: CategoryDistribution;
  priority_distribution: PriorityDistribution;
}