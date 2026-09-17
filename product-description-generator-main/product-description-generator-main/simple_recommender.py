import csv
import math
import os
import time
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import gradio as gr

class SimpleMarketingRecommender:
    def __init__(self, data_path='data/marketing_strategies.csv', trend_data_path='data/marketing_trends.csv'):
        self.data_path = data_path
        self.trend_data_path = trend_data_path
        self.strategies = []
        self.trend_data = []
        self.trend_models = {}
        self.load_data()
        self.load_trend_data()
        self.train_trend_models()
    
    def load_data(self):
        """Load marketing strategies data from CSV"""
        if not os.path.exists(self.data_path):
            print(f"Error: Data file not found at {self.data_path}")
            return
            
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.strategies = list(reader)
                print(f"Loaded {len(self.strategies)} strategies from {self.data_path}")
                
            # Convert numeric strings to integers
            numeric_fields = [
                'strategy_id', 'budget_required', 'technical_expertise', 
                'time_investment', 'conversion_rate', 'brand_awareness', 
                'lead_generation', 'customer_retention', 'target_audience_size'
            ]
            
            for strategy in self.strategies:
                for field in numeric_fields:
                    if field in strategy:
                        try:
                            strategy[field] = int(strategy[field])
                        except (ValueError, TypeError):
                            print(f"Warning: Could not convert {field} to integer for strategy {strategy.get('strategy_name', 'unknown')}")
                            strategy[field] = 0
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def load_trend_data(self):
        """Load historical trend data for marketing strategies"""
        if not os.path.exists(self.trend_data_path):
            print(f"Error: Trend data file not found at {self.trend_data_path}")
            return
            
        try:
            with open(self.trend_data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.trend_data = list(reader)
                print(f"Loaded {len(self.trend_data)} trend data points from {self.trend_data_path}")
                
            # Convert numeric strings to floats
            for trend in self.trend_data:
                try:
                    trend['date'] = datetime.strptime(trend['date'], '%Y-%m-%d')
                    trend['effectiveness'] = float(trend['effectiveness'])
                    trend['cost_efficiency'] = float(trend['cost_efficiency'])
                    trend['adoption_rate'] = float(trend['adoption_rate'])
                    trend['strategy_id'] = int(trend['strategy_id'])
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not convert data for trend point: {e}")
                    continue
        except Exception as e:
            print(f"Error loading trend data: {e}")
    
    def train_trend_models(self):
        """Train regression models for each strategy's trends"""
        print("\n🔄 Training trend models...")
        trained_count = 0
        skipped_count = 0
        
        for strategy in self.strategies:
            try:
                strategy_id = int(strategy['strategy_id'])
                strategy_trends = [t for t in self.trend_data if int(t['strategy_id']) == strategy_id]
                
                if len(strategy_trends) < 2:
                    skipped_count += 1
                    continue
                    
                # Prepare data for training
                X = np.array([(t['date'] - min(t['date'] for t in strategy_trends)).days 
                             for t in strategy_trends]).reshape(-1, 1)
                y_effectiveness = np.array([t['effectiveness'] for t in strategy_trends])
                y_cost = np.array([t['cost_efficiency'] for t in strategy_trends])
                y_adoption = np.array([t['adoption_rate'] for t in strategy_trends])
                
                # Train models
                self.trend_models[strategy_id] = {
                    'effectiveness': LinearRegression().fit(X, y_effectiveness),
                    'cost_efficiency': LinearRegression().fit(X, y_cost),
                    'adoption_rate': LinearRegression().fit(X, y_adoption)
                }
                trained_count += 1
                
            except Exception as e:
                print(f"⚠️ Error training model for strategy {strategy_id}: {e}")
                skipped_count += 1
                continue
            
        print(f"✅ Trained models for {trained_count} strategies")
        if skipped_count > 0:
            print(f"⚠️ Skipped {skipped_count} strategies due to insufficient data or errors")
    
    def predict_trend_metrics(self, strategy_id, days_ahead=30):
        """Predict future trend metrics for a strategy"""
        if strategy_id not in self.trend_models:
            return None
            
        models = self.trend_models[strategy_id]
        latest_date = max(t['date'] for t in self.trend_data if t['strategy_id'] == strategy_id)
        days_since_start = (latest_date - min(t['date'] for t in self.trend_data 
                                            if t['strategy_id'] == strategy_id)).days
        
        # Predict for multiple time points to identify growth rate
        future_days = np.array([[days_since_start + i] for i in range(1, days_ahead + 1)])
        
        # Get predictions for all future days
        effectiveness_predictions = models['effectiveness'].predict(future_days)
        cost_predictions = models['cost_efficiency'].predict(future_days)
        adoption_predictions = models['adoption_rate'].predict(future_days)
        
        # Calculate growth rates
        initial_effectiveness = effectiveness_predictions[0]
        final_effectiveness = effectiveness_predictions[-1]
        growth_rate = ((final_effectiveness - initial_effectiveness) / initial_effectiveness) * 100
        
        # Calculate acceleration (second derivative)
        effectiveness_acceleration = np.gradient(np.gradient(effectiveness_predictions))
        is_accelerating = np.mean(effectiveness_acceleration) > 0
        
        # Find when the strategy becomes trending (effectiveness crosses threshold)
        trending_threshold = 0.5  # Lower threshold to catch more potential trends
        trending_week = None
        for i, pred in enumerate(effectiveness_predictions):
            if pred >= trending_threshold:
                trending_week = (i + 1) // 7  # Convert days to weeks
                break
        
        # Determine if strategy is trending based on multiple factors
        is_trending = (
            effectiveness_predictions[-1] >= trending_threshold and
            growth_rate > 2.0 and  # Lower minimum growth rate
            adoption_predictions[-1] > 0.4  # Lower minimum adoption rate
        )
        
        return {
            'effectiveness': effectiveness_predictions[-1],
            'cost_efficiency': cost_predictions[-1],
            'adoption_rate': adoption_predictions[-1],
            'growth_rate': growth_rate,
            'trending_week': trending_week,
            'is_trending': is_trending,
            'acceleration': np.mean(effectiveness_acceleration)
        }
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
            
        # Return cosine similarity
        return dot_product / (magnitude1 * magnitude2)
    
    def get_recommendations(self, user_preferences, top_n=5, include_trends=True):
        """
        Get personalized recommendations based on user preferences and trend analysis
        
        Args:
            user_preferences: dict with the following keys:
                - budget_amount: monthly budget amount in dollars
                - daily_hours: number of hours available per day
                - technical_skill: 1-5 (1=beginner, 5=expert)
                - goal: one of ['conversion', 'awareness', 'leads', 'retention']
                - industry: string with the industry name
                - audience_size: 1-5 (1=very small, 5=very large)
            top_n: number of recommendations to return
            include_trends: whether to include trend predictions in recommendations
            
        Returns:
            List of recommended strategies with trend predictions
        """
        # Create user profile vector
        user_profile = [0] * 8
        
        # Convert budget amount to a level (1-5)
        budget_amount = user_preferences.get('budget_amount', 2000)
        if budget_amount < 500:
            budget_level = 1
        elif budget_amount < 1000:
            budget_level = 2
        elif budget_amount < 2000:
            budget_level = 3
        elif budget_amount < 5000:
            budget_level = 4
        else:
            budget_level = 5
            
        # Map budget to budget_required (inverse relationship)
        user_profile[0] = 6 - budget_level  # Inverse: higher budget = lower concern
        
        # Map technical skill to technical_expertise (inverse relationship)
        user_profile[1] = 6 - user_preferences['technical_skill']  # Inverse: higher skill = lower concern
        
        # Map daily hours to time_investment (inverse relationship)
        daily_hours = user_preferences.get('daily_hours', 8)
        if daily_hours < 2:
            time_level = 1
        elif daily_hours < 4:
            time_level = 2
        elif daily_hours < 6:
            time_level = 3
        elif daily_hours < 8:
            time_level = 4
        else:
            time_level = 5
        user_profile[2] = 6 - time_level  # Inverse: more time = lower concern
        
        # Map goal to specific features
        goal_mapping = {
            'conversion': 3,  # index of conversion_rate
            'awareness': 4,   # index of brand_awareness
            'leads': 5,       # index of lead_generation
            'retention': 6    # index of customer_retention
        }
        
        # Set default values for goals
        for i in range(3, 7):
            user_profile[i] = 3  # Set default value
            
        # Emphasize the specific goal
        if user_preferences['goal'] in goal_mapping:
            goal_index = goal_mapping[user_preferences['goal']]
            user_profile[goal_index] = 5  # Boost the specific goal
        
        # Map audience size
        user_profile[7] = user_preferences['audience_size']
        
        # Calculate similarity with all strategies
        strategy_similarities = []
        
        for strategy in self.strategies:
            # Extract strategy features
            strategy_features = [
                strategy['budget_required'],
                strategy['technical_expertise'],
                strategy['time_investment'],
                strategy['conversion_rate'],
                strategy['brand_awareness'],
                strategy['lead_generation'],
                strategy['customer_retention'],
                strategy['target_audience_size']
            ]
            
            # Calculate similarity
            similarity = self.cosine_similarity(user_profile, strategy_features)
            
            # Check if industry matches
            industry_match = False
            if user_preferences.get('industry'):
                industries = strategy['best_for_industry'].replace('"', '').split(',')
                industry_match = user_preferences['industry'] in industries or 'All' in industries
            else:
                industry_match = True  # No industry filter
                
            # Add to results if industry matches
            if industry_match:
                strategy_similarities.append((strategy, similarity))
        
        # Sort by similarity score (descending)
        strategy_similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N recommendations
        recommendations = strategy_similarities[:top_n]
        
        if include_trends:
            # Add trend predictions to each recommendation
            enhanced_recommendations = []
            for strategy, similarity in recommendations:
                trend_metrics = self.predict_trend_metrics(strategy['strategy_id'])
                if trend_metrics:
                    strategy['trend_metrics'] = trend_metrics
                    # Add trending status
                    strategy['is_trending'] = trend_metrics['is_trending']
                    strategy['trending_week'] = trend_metrics['trending_week']
                    strategy['growth_rate'] = trend_metrics['growth_rate']
                    strategy['acceleration'] = trend_metrics['acceleration']
                enhanced_recommendations.append((strategy, similarity))
            
            # Sort by growth rate and acceleration
            enhanced_recommendations.sort(
                key=lambda x: (
                    x[0].get('growth_rate', 0) * 0.7 + 
                    x[0].get('acceleration', 0) * 0.3
                ),
                reverse=True
            )
            
            return enhanced_recommendations
        
        return recommendations
    
    def get_strategy_details(self, strategy_id):
        """Get detailed information about a specific strategy"""
        for strategy in self.strategies:
            if strategy['strategy_id'] == strategy_id:
                return strategy
        return None

def predict_product_trend(product_name, category, initial_price, marketing_budget, 
                        time_period, seasonality_factor, competition_level):
    """Generate product trend predictions based on inputs"""
    try:
        # Convert inputs to appropriate types
        initial_price = float(initial_price)
        marketing_budget = float(marketing_budget)
        time_period = int(time_period)
        seasonality_factor = float(seasonality_factor)
        competition_level = float(competition_level)
        
        # Generate prediction data
        dates = [datetime.now() + timedelta(weeks=i) for i in range(time_period)]
        
        # Base trend with seasonality
        base_trend = []
        for i in range(time_period):
            # Start with a base value
            value = initial_price * 0.10  # 10% of price as base sales
            
            # Add growth over time (higher marketing budget = faster growth)
            growth = (marketing_budget / 1000) * (i / time_period) * 1.5
            
            # Add seasonality effect (varies based on seasonality factor)
            season = seasonality_factor * np.sin(i * 2 * np.pi / 52)  # 52 weeks in a year
            
            # Competition reduces growth over time
            competition_effect = 1.0 - (competition_level * i / (time_period * 10))
            
            # Calculate prediction with all factors
            prediction = (value + growth + season) * competition_effect
            base_trend.append(max(0, prediction))  # Ensure non-negative
        
        # Create optimistic and pessimistic scenarios
        optimistic = [val * 1.3 for val in base_trend]
        pessimistic = [val * 0.7 for val in base_trend]
        
        # Calculate ROI
        total_sales = sum(base_trend)
        total_revenue = total_sales * initial_price
        roi = ((total_revenue - marketing_budget) / marketing_budget) * 100 if marketing_budget > 0 else 0
        
        # Generate plot
        fig = plt.figure(figsize=(10, 6))
        plt.plot([d.strftime('%m/%d') for d in dates], base_trend, 'b-', label='Expected')
        plt.plot([d.strftime('%m/%d') for d in dates], optimistic, 'g--', label='Optimistic')
        plt.plot([d.strftime('%m/%d') for d in dates], pessimistic, 'r--', label='Pessimistic')
        plt.xlabel('Date')
        plt.ylabel('Projected Sales')
        plt.title(f'Sales Forecast for {product_name}')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Create directory if it doesn't exist
        os.makedirs("temp_charts", exist_ok=True)
        
        # Save to a temporary file - use absolute path for Gradio
        temp_file = os.path.join(os.path.abspath("temp_charts"), f"chart_{int(time.time())}.png")
        plt.savefig(temp_file)
        plt.close()
        
        # Create summary text
        summary = f"""## Product Trend Forecast: {product_name}

**Category:** {category}
**Time Period:** {time_period} weeks
**Initial Price:** ${initial_price:.2f}
**Marketing Budget:** ${marketing_budget:.2f}

### Forecast Results:
- **Peak Sales (Expected):** {max(base_trend):.1f} units/week
- **Projected Total Sales:** {sum(base_trend):.1f} units
- **Estimated Revenue:** ${sum(base_trend) * initial_price:.2f}
- **Projected ROI:** {roi:.1f}%

### Key Factors:
- Seasonality Impact: {"High" if seasonality_factor > 0.5 else "Medium" if seasonality_factor > 0.2 else "Low"}
- Competition Level: {"High" if competition_level > 0.7 else "Medium" if competition_level > 0.4 else "Low"}
"""
        
        print(f"Saved chart to: {temp_file}")
        return temp_file, summary
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error in predict_product_trend: {error_msg}")
        # Return a placeholder image path and error message
        placeholder_img = "data/placeholder_error.png"
        if not os.path.exists("data"):
            os.makedirs("data", exist_ok=True)
        if not os.path.exists(placeholder_img):
            # Create a simple error image
            fig = plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "Error generating chart", ha='center', va='center', fontsize=16)
            plt.axis('off')
            plt.savefig(placeholder_img)
            plt.close()
        return placeholder_img, f"Error generating product trend forecast: {str(e)}"

# Add this to your startup code
def clean_old_chart_files(directory="temp_charts", max_age_hours=24):
    """Remove chart files older than the specified age"""
    try:
        if not os.path.exists(directory):
            return
            
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and filename.startswith("chart_"):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    os.remove(filepath)
                    print(f"Removed old chart file: {filename}")
    except Exception as e:
        print(f"Error cleaning chart files: {e}")

# Example usage
if __name__ == "__main__":
    # Clean old chart files
    clean_old_chart_files()
    
    # Create required directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("generated_gifs", exist_ok=True)
    os.makedirs("generated_images", exist_ok=True)
    os.makedirs("temp_charts", exist_ok=True)
    
    # Launch Gradio app
    with gr.Blocks() as demo:
        with gr.Tab("Product Trend Predictor"):
            gr.Markdown("### 📈 Product Trend & Sales Forecast")
            gr.Markdown("Predict product sales trends based on key parameters")
            
            with gr.Row():
                with gr.Column():
                    trend_product_name = gr.Textbox(
                        label="Product Name",
                        placeholder="Enter product name",
                        value="New Product X"
                    )
                    trend_category = gr.Dropdown(
                        label="Product Category",
                        choices=["Electronics", "Clothing", "Food & Beverage", "Home Goods", 
                                 "Beauty & Personal Care", "Sports & Fitness", "Other"],
                        value="Electronics"
                    )
                    trend_initial_price = gr.Slider(
                        label="Initial Price ($)",
                        minimum=1.0,
                        maximum=1000.0,
                        value=49.99,
                        step=1.0
                    )
                    trend_marketing_budget = gr.Slider(
                        label="Marketing Budget ($)",
                        minimum=100.0,
                        maximum=10000.0,
                        value=2000.0,
                        step=100.0
                    )
                    trend_time_period = gr.Slider(
                        label="Time Period (weeks)",
                        minimum=4,
                        maximum=52,
                        value=26,
                        step=1
                    )
                    trend_seasonality_factor = gr.Slider(
                        label="Seasonality Impact (0-1)",
                        minimum=0.0,
                        maximum=1.0,
                        value=0.3,
                        step=0.1
                    )
                    trend_competition_level = gr.Slider(
                        label="Market Competition Level (0-1)",
                        minimum=0.0,
                        maximum=1.0,
                        value=0.5,
                        step=0.1
                    )
                    predict_trend_btn = gr.Button("Generate Trend Forecast", variant="primary")
                
                with gr.Column():
                    # Change from gr.Image() to gr.Image(type="filepath")
                    trend_chart_output = gr.Image(label="Trend Forecast Chart", type="filepath")
                    trend_summary_output = gr.Markdown(label="Forecast Summary")
            
            # Connect the button to the prediction function
            predict_trend_btn.click(
                fn=predict_product_trend,
                inputs=[
                    trend_product_name,
                    trend_category,
                    trend_initial_price,
                    trend_marketing_budget,
                    trend_time_period,
                    trend_seasonality_factor,
                    trend_competition_level
                ],
                outputs=[trend_chart_output, trend_summary_output]
            )
    
    demo.launch()