from pydantic import BaseModel
from datetime import datetime, date
from typing import Dict, List, Optional

class AggregateHabitStats(BaseModel):
    total_habits: int
    active_habits: int
    completed_today: int
    completion_rate: float
    average_streak: float
    best_streak: int

class HabitFrequencyDistribution(BaseModel):
    daily: int
    weekly: int
    monthly: int

class HabitCompletionTrend(BaseModel):
    date: date
    completed: int

class AggregateHabitAnalytics(BaseModel):
    stats: AggregateHabitStats
    frequency_distribution: HabitFrequencyDistribution
    completion_trend: List[HabitCompletionTrend]
    category_completion: Dict[str, int]