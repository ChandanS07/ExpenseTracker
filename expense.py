import uuid
from datetime import datetime, timedelta
import json
from collections import defaultdict

class Expense:
    """Class representing an expense."""
    
    def __init__(self, amount, date, description, category, id=None):
        """Initialize an expense."""
        self.id = id or str(uuid.uuid4())
        self.amount = amount
        self.date = date if isinstance(date, datetime) else datetime.strptime(date, '%Y-%m-%d')
        self.description = description
        self.category = category
    
    def to_dict(self):
        """Convert expense to dictionary."""
        return {
            'id': self.id,
            'amount': self.amount,
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description,
            'category': self.category
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create expense from dictionary."""
        return cls(
            id=data.get('id'),
            amount=data.get('amount'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d'),
            description=data.get('description'),
            category=data.get('category')
        )

class ExpenseManager:
    """Class for managing expenses."""
    
    def __init__(self):
        """Initialize expense manager."""
        self.expenses = {}
    
    def add_expense(self, expense):
        """Add an expense."""
        self.expenses[expense.id] = expense
        return expense
    
    def get_expense(self, id):
        """Get an expense by ID."""
        return self.expenses.get(id)
    
    def update_expense(self, expense):
        """Update an expense."""
        if expense.id in self.expenses:
            self.expenses[expense.id] = expense
            return True
        return False
    
    def delete_expense(self, id):
        """Delete an expense."""
        if id in self.expenses:
            del self.expenses[id]
            return True
        return False
    
    def get_all_expenses(self):
        """Get all expenses."""
        return list(self.expenses.values())
    
    def get_filtered_expenses(self, category=None, start_date=None, end_date=None, sort_by='date', sort_order='desc'):
        """Get filtered expenses."""
        expenses = self.get_all_expenses()
        
        # Apply category filter
        if category:
            expenses = [e for e in expenses if e.category == category]
        
        # Apply date filters
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            expenses = [e for e in expenses if e.date >= start_date]
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            expenses = [e for e in expenses if e.date <= end_date]
        
        # Apply sorting
        if sort_by == 'amount':
            expenses.sort(key=lambda e: e.amount, reverse=(sort_order == 'desc'))
        elif sort_by == 'date':
            expenses.sort(key=lambda e: e.date, reverse=(sort_order == 'desc'))
        elif sort_by == 'category':
            expenses.sort(key=lambda e: e.category, reverse=(sort_order == 'desc'))
        
        return expenses
    
    def get_stats(self, period='month'):
        """Get expense statistics for the given period."""
        today = datetime.now()
        
        if period == 'week':
            start_date = today - timedelta(days=today.weekday())
        elif period == 'month':
            start_date = datetime(today.year, today.month, 1)
        elif period == 'year':
            start_date = datetime(today.year, 1, 1)
        else:
            start_date = datetime(1970, 1, 1)  # All time
        
        filtered_expenses = [e for e in self.expenses.values() if e.date >= start_date]
        
        if not filtered_expenses:
            return {
                'total': 0,
                'average_per_day': 0,
                'count': 0
            }
        
        total = sum(e.amount for e in filtered_expenses)
        days = max(1, (today - start_date).days)
        
        return {
            'total': round(total, 2),
            'average_per_day': round(total / days, 2),
            'count': len(filtered_expenses)
        }
    
    def get_category_breakdown(self, period='month'):
        """Get category breakdown for the given period."""
        today = datetime.now()
        
        if period == 'week':
            start_date = today - timedelta(days=today.weekday())
        elif period == 'month':
            start_date = datetime(today.year, today.month, 1)
        elif period == 'year':
            start_date = datetime(today.year, 1, 1)
        else:
            start_date = datetime(1970, 1, 1)  # All time
        
        filtered_expenses = [e for e in self.expenses.values() if e.date >= start_date]
        
        category_totals = defaultdict(float)
        for expense in filtered_expenses:
            category_totals[expense.category] += expense.amount
        
        # Format for Chart.js
        labels = list(category_totals.keys())
        data = [round(category_totals[label], 2) for label in labels]
        
        return {
            'labels': labels,
            'data': data
        }
    
    def get_monthly_trend(self, months=6):
        """Get monthly expense trend for the last N months."""
        today = datetime.now()
        months_labels = []
        months_data = []
        
        # Generate data for each month
        for i in range(months - 1, -1, -1):
            # Calculate the month
            month_date = datetime(today.year, today.month, 1) - timedelta(days=i * 30)
            month_label = month_date.strftime('%b %Y')
            months_labels.append(month_label)
            
            # Get expenses for that month
            month_start = datetime(month_date.year, month_date.month, 1)
            month_end = datetime(month_date.year, month_date.month + 1, 1) - timedelta(days=1) if month_date.month < 12 else datetime(month_date.year + 1, 1, 1) - timedelta(days=1)
            
            month_expenses = [e for e in self.expenses.values() 
                             if e.date >= month_start and e.date <= month_end]
            
            month_total = sum(e.amount for e in month_expenses)
            months_data.append(round(month_total, 2))
        
        return {
            'labels': months_labels,
            'data': months_data
        }
    
    def get_financial_insights(self):
        """Get financial insights based on spending patterns."""
        all_expenses = self.get_all_expenses()
        
        if not all_expenses:
            return {
                'top_spending_category': 'No data available',
                'biggest_expense': 'No data available',
                'average_transaction': 0,
                'spending_trend': 'No data available'
            }
        
        # Calculate top spending category
        category_totals = defaultdict(float)
        for expense in all_expenses:
            category_totals[expense.category] += expense.amount
        
        top_category = max(category_totals.items(), key=lambda x: x[1])
        
        # Find biggest expense
        biggest_expense = max(all_expenses, key=lambda e: e.amount)
        
        # Calculate average transaction
        average_transaction = sum(e.amount for e in all_expenses) / len(all_expenses)
        
        # Determine spending trend
        # Sort expenses by date
        sorted_expenses = sorted(all_expenses, key=lambda e: e.date)
        
        # If we have enough data, calculate trend
        if len(sorted_expenses) >= 2:
            # Split into two halves
            mid_point = len(sorted_expenses) // 2
            first_half = sorted_expenses[:mid_point]
            second_half = sorted_expenses[mid_point:]
            
            first_half_avg = sum(e.amount for e in first_half) / len(first_half)
            second_half_avg = sum(e.amount for e in second_half) / len(second_half)
            
            if second_half_avg > first_half_avg * 1.1:
                trend = "Increasing"
            elif second_half_avg < first_half_avg * 0.9:
                trend = "Decreasing"
            else:
                trend = "Stable"
        else:
            trend = "Not enough data"
        
        return {
            'top_spending_category': f"{top_category[0]} (${top_category[1]:.2f})",
            'biggest_expense': f"{biggest_expense.description} (${biggest_expense.amount:.2f})",
            'average_transaction': round(average_transaction, 2),
            'spending_trend': trend
        }
