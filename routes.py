import uuid
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from models import User, Expense
from forms import LoginForm, RegistrationForm, ExpenseForm

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Log out a user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('welcome'))

@app.route('/')
def welcome():
    """Show welcome page for non-authenticated users or dashboard for authenticated users."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('welcome.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Render the dashboard with expense summary and charts."""
    return render_template('dashboard.html', categories=categories)

@app.route('/expenses')
@login_required
def expenses():
    """Show all expenses with filtering and sorting."""
    # Get filter parameters
    category = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Get expenses
    query = Expense.query.filter_by(user_id=current_user.id)
    
    # Apply category filter
    if category:
        query = query.filter_by(category=category)
    
    # Apply date filters
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Expense.date >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(Expense.date <= end_date_obj)
    
    # Apply sorting
    if sort_by == 'amount':
        query = query.order_by(Expense.amount.desc() if sort_order == 'desc' else Expense.amount)
    elif sort_by == 'date':
        query = query.order_by(Expense.date.desc() if sort_order == 'desc' else Expense.date)
    elif sort_by == 'category':
        query = query.order_by(Expense.category.desc() if sort_order == 'desc' else Expense.category)
    
    # Execute query
    filtered_expenses = query.all()
    
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
@login_required
def add_expense():
    """Add a new expense."""
    form = ExpenseForm()
    form.category.choices = [(cat, cat) for cat in categories]
    
    if form.validate_on_submit():
        expense = Expense(
            amount=form.amount.data,
            date=form.date.data,
            description=form.description.data,
            category=form.category.data,
            user_id=current_user.id
        )
        
        db.session.add(expense)
        db.session.commit()
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    return render_template('add_expense.html', form=form, categories=categories)

@app.route('/expense/edit/<expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    """Edit an existing expense."""
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    
    form = ExpenseForm()
    form.category.choices = [(cat, cat) for cat in categories]
    
    if form.validate_on_submit():
        expense.amount = form.amount.data
        expense.date = form.date.data
        expense.description = form.description.data
        expense.category = form.category.data
        
        db.session.commit()
        
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expenses'))
    elif request.method == 'GET':
        form.amount.data = expense.amount
        form.date.data = expense.date
        form.description.data = expense.description
        form.category.data = expense.category
    
    return render_template('edit_expense.html', form=form, expense=expense, categories=categories)

@app.route('/expense/delete/<expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    """Delete an expense."""
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(expense)
    db.session.commit()
    
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses'))

@app.route('/api/expense-stats')
@login_required
def expense_stats():
    """API to get expense statistics for charts."""
    period = request.args.get('period', 'month')
    today = datetime.now()
    
    if period == 'week':
        start_date = today - timedelta(days=today.weekday())
    elif period == 'month':
        start_date = datetime(today.year, today.month, 1)
    elif period == 'year':
        start_date = datetime(today.year, 1, 1)
    else:
        start_date = datetime(1970, 1, 1)  # All time
    
    # Get expenses for the period
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date
    ).all()
    
    if not expenses:
        return jsonify({
            'total': 0,
            'average_per_day': 0,
            'count': 0
        })
    
    total = sum(expense.amount for expense in expenses)
    days = max(1, (today - start_date).days)
    
    return jsonify({
        'total': round(total, 2),
        'average_per_day': round(total / days, 2),
        'count': len(expenses)
    })

@app.route('/api/category-breakdown')
@login_required
def category_breakdown():
    """API to get category breakdown for charts."""
    period = request.args.get('period', 'month')
    today = datetime.now()
    
    if period == 'week':
        start_date = today - timedelta(days=today.weekday())
    elif period == 'month':
        start_date = datetime(today.year, today.month, 1)
    elif period == 'year':
        start_date = datetime(today.year, 1, 1)
    else:
        start_date = datetime(1970, 1, 1)  # All time
    
    # Get expenses for the period
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date
    ).all()
    
    category_totals = {}
    for expense in expenses:
        if expense.category not in category_totals:
            category_totals[expense.category] = 0
        category_totals[expense.category] += expense.amount
    
    # Format for Chart.js
    labels = list(category_totals.keys())
    data = [round(category_totals[label], 2) for label in labels]
    
    return jsonify({
        'labels': labels,
        'data': data
    })

@app.route('/api/monthly-trend')
@login_required
def monthly_trend():
    """API to get monthly trend data for charts."""
    months = int(request.args.get('months', 6))
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
        
        expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.date >= month_start,
            Expense.date <= month_end
        ).all()
        
        month_total = sum(expense.amount for expense in expenses)
        months_data.append(round(month_total, 2))
    
    return jsonify({
        'labels': months_labels,
        'data': months_data
    })

@app.route('/api/financial-insights')
@login_required
def financial_insights():
    """API to get financial insights."""
    # Get all expenses for the user
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    
    if not expenses:
        return jsonify({
            'top_spending_category': 'No data available',
            'biggest_expense': 'No data available',
            'average_transaction': 0,
            'spending_trend': 'No data available'
        })
    
    # Calculate top spending category
    category_totals = {}
    for expense in expenses:
        if expense.category not in category_totals:
            category_totals[expense.category] = 0
        category_totals[expense.category] += expense.amount
    
    top_category = max(category_totals.items(), key=lambda x: x[1])
    
    # Find biggest expense
    biggest_expense = max(expenses, key=lambda e: e.amount)
    
    # Calculate average transaction
    average_transaction = sum(e.amount for e in expenses) / len(expenses)
    
    # Determine spending trend
    sorted_expenses = sorted(expenses, key=lambda e: e.date)
    
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
    
    return jsonify({
        'top_spending_category': f"{top_category[0]} (${top_category[1]:.2f})",
        'biggest_expense': f"{biggest_expense.description} (${biggest_expense.amount:.2f})",
        'average_transaction': round(average_transaction, 2),
        'spending_trend': trend
    })