import os
import logging
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from datetime import datetime
from expense import ExpenseManager, Expense

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize the expense manager
expense_manager = ExpenseManager()

# Add some categories
categories = [
    "Food & Dining", 
    "Transportation", 
    "Entertainment", 
    "Shopping", 
    "Utilities", 
    "Housing", 
    "Healthcare", 
    "Education", 
    "Travel", 
    "Miscellaneous"
]

@app.route('/')
def index():
    """Render the dashboard with expense summary and charts."""
    return render_template('dashboard.html', categories=categories)

@app.route('/expenses')
def expenses():
    """Show all expenses with filtering and sorting."""
    # Get filter parameters
    category = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Apply filters and sorting
    filtered_expenses = expense_manager.get_filtered_expenses(
        category=category, 
        start_date=start_date, 
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return render_template(
        'expenses.html',
        expenses=filtered_expenses,
        categories=categories,
        category=category,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order
    )

@app.route('/expense/add', methods=['GET', 'POST'])
def add_expense():
    """Add a new expense."""
    if request.method == 'POST':
        try:
            # Parse form data
            amount = float(request.form.get('amount'))
            if amount <= 0:
                flash('Amount must be greater than zero', 'danger')
                return render_template('add_expense.html', categories=categories)
                
            date_str = request.form.get('date')
            description = request.form.get('description')
            category = request.form.get('category')
            
            # Validate data
            if not date_str or not description or not category:
                flash('All fields are required', 'danger')
                return render_template('add_expense.html', categories=categories)
            
            # Parse date
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Create expense
            expense = Expense(
                amount=amount,
                date=date,
                description=description,
                category=category
            )
            
            # Add to manager
            expense_manager.add_expense(expense)
            
            flash('Expense added successfully!', 'success')
            return redirect(url_for('expenses'))
        except ValueError as e:
            flash(f'Error adding expense: {str(e)}', 'danger')
    
    return render_template('add_expense.html', categories=categories)

@app.route('/expense/edit/<expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    """Edit an existing expense."""
    expense = expense_manager.get_expense(expense_id)
    
    if not expense:
        flash('Expense not found', 'danger')
        return redirect(url_for('expenses'))
    
    if request.method == 'POST':
        try:
            # Parse form data
            amount = float(request.form.get('amount'))
            if amount <= 0:
                flash('Amount must be greater than zero', 'danger')
                return render_template('edit_expense.html', expense=expense, categories=categories)
                
            date_str = request.form.get('date')
            description = request.form.get('description')
            category = request.form.get('category')
            
            # Validate data
            if not date_str or not description or not category:
                flash('All fields are required', 'danger')
                return render_template('edit_expense.html', expense=expense, categories=categories)
            
            # Parse date
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Update expense
            updated_expense = Expense(
                id=expense_id,
                amount=amount,
                date=date,
                description=description,
                category=category
            )
            
            expense_manager.update_expense(updated_expense)
            
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('expenses'))
        except ValueError as e:
            flash(f'Error updating expense: {str(e)}', 'danger')
    
    return render_template('edit_expense.html', expense=expense, categories=categories)

@app.route('/expense/delete/<expense_id>', methods=['POST'])
def delete_expense(expense_id):
    """Delete an expense."""
    expense_manager.delete_expense(expense_id)
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses'))

@app.route('/api/expense-stats')
def expense_stats():
    """API to get expense statistics for charts."""
    period = request.args.get('period', 'month')
    stats = expense_manager.get_stats(period)
    return jsonify(stats)

@app.route('/api/category-breakdown')
def category_breakdown():
    """API to get category breakdown for charts."""
    period = request.args.get('period', 'month')
    breakdown = expense_manager.get_category_breakdown(period)
    return jsonify(breakdown)

@app.route('/api/monthly-trend')
def monthly_trend():
    """API to get monthly trend data for charts."""
    months = int(request.args.get('months', 6))
    trend = expense_manager.get_monthly_trend(months)
    return jsonify(trend)

@app.route('/api/financial-insights')
def financial_insights():
    """API to get financial insights."""
    insights = expense_manager.get_financial_insights()
    return jsonify(insights)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
